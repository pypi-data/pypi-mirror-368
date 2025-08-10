import json
import logging
import threading
import time
import typing
from collections import defaultdict
from collections.abc import Callable

from .api import SHCAPI, JSONRPCError
from .device import SHCDevice
from .device_helper import SHCDeviceHelper
from .domain_impl import SHCIntrusionSystem
from .exceptions import SHCAuthenticationError, SHCSessionError
from .information import SHCInformation
from .room import SHCRoom
from .scenario import SHCScenario
from .message import SHCMessage
from .emma import SHCEmma
from .userdefinedstate import SHCUserDefinedState
from .services_impl import SUPPORTED_DEVICE_SERVICE_IDS

logger = logging.getLogger("boschshcpy")


class SHCSession:
    def __init__(self, controller_ip: str, certificate, key, lazy=False, zeroconf=None):
        # API
        self._api = SHCAPI(
            controller_ip=controller_ip, certificate=certificate, key=key
        )
        self._device_helper = SHCDeviceHelper(self._api)

        # Subscription status
        self._poll_id = None

        # SHC Information
        self._shc_information = None
        self._zeroconf = zeroconf

        # All devices
        self._rooms_by_id = {}
        self._scenarios_by_id = {}
        self._devices_by_id = {}
        self._services_by_device_id = defaultdict(list)
        self._domains_by_id = {}
        self._messages_by_id = {}
        self._userdefinedstates_by_id = {}
        self._subscribers = []
        self._emma: SHCEmma = SHCEmma(self._api)

        if not lazy:
            self._enumerate_all()

        self._polling_thread = None
        self._stop_polling_thread = False

        # Stop polling function
        self.reset_connection_listener = None

        self._scenario_callbacks = {}
        self._userdefinedstate_callbacks = defaultdict(list)

    def _enumerate_all(self):
        self.authenticate()
        self._enumerate_services()
        self._enumerate_devices()
        self._enumerate_rooms()
        self._enumerate_scenarios()
        self._enumerate_messages()
        self._enumerate_userdefinedstates()
        self._initialize_domains()
        self._initialize_emma()

    def _add_device(self, raw_device, update_services=False) -> SHCDevice:
        device_id = raw_device["id"]

        if update_services:
            self._services_by_device_id.pop(device_id, None)
            raw_services = self._api.get_device_services(device_id)
            for service in raw_services:
                if service["id"] not in SUPPORTED_DEVICE_SERVICE_IDS:
                    continue
                device_id = service["deviceId"]
                self._services_by_device_id[device_id].append(service)

        if not self._services_by_device_id[device_id]:
            logger.debug(
                f"Skipping device id {device_id} which has no services that are supported by this library"
            )
            return None

        device = self._device_helper.device_init(
            raw_device, self._services_by_device_id[device_id]
        )
        self._devices_by_id[device_id] = device
        return device

    def _update_device(self, raw_device):
        device_id = raw_device["id"]
        self._devices_by_id[device_id].update_raw_information(raw_device)

    def _enumerate_services(self):
        raw_services = self._api.get_services()
        for service in raw_services:
            if service["id"] not in SUPPORTED_DEVICE_SERVICE_IDS:
                continue
            device_id = service["deviceId"]
            self._services_by_device_id[device_id].append(service)

    def _enumerate_devices(self):
        raw_devices = self._api.get_devices()

        for raw_device in raw_devices:
            self._add_device(raw_device)

    def _enumerate_rooms(self):
        raw_rooms = self._api.get_rooms()
        for raw_room in raw_rooms:
            room_id = raw_room["id"]
            room = SHCRoom(api=self._api, raw_room=raw_room)
            self._rooms_by_id[room_id] = room

    def _enumerate_scenarios(self):
        raw_scenarios = self._api.get_scenarios()
        for raw_scenario in raw_scenarios:
            scenario_id = raw_scenario["id"]
            scenario = SHCScenario(api=self._api, raw_scenario=raw_scenario)
            self._scenarios_by_id[scenario_id] = scenario

    def _enumerate_messages(self):
        raw_messages = self._api.get_messages()
        for raw_message in raw_messages:
            message_id = raw_message["id"]
            message = SHCMessage(api=self._api, raw_message=raw_message)
            self._messages_by_id[message_id] = message

    def _enumerate_userdefinedstates(self):
        raw_states = self._api.get_userdefinedstates()
        for raw_state in raw_states:
            userdefinedstate_id = raw_state["id"]
            userdefinedstate = SHCUserDefinedState(
                api=self._api, info=self.information, raw_state=raw_state
            )
            self._userdefinedstates_by_id[userdefinedstate_id] = userdefinedstate

    def _initialize_domains(self):
        self._domains_by_id["IDS"] = SHCIntrusionSystem(
            self._api,
            self._api.get_domain_intrusion_detection(),
            self.information.macAddress,
        )

    def _initialize_emma(self):
        self._emma = SHCEmma(self._api, self._shc_information, None)

    def _long_poll(self, wait_seconds=10):
        if self._poll_id is None:
            self._poll_id = self.api.long_polling_subscribe()
            logger.debug(f"Subscribed for long poll. Poll id: {self._poll_id}")
        try:
            raw_results = self.api.long_polling_poll(self._poll_id, wait_seconds)
            for raw_result in raw_results:
                self._process_long_polling_poll_result(raw_result)

            return True
        except JSONRPCError as json_rpc_error:
            if json_rpc_error.code == -32001:
                self._poll_id = None
                logger.warning(
                    f"SHC claims unknown poll id. Invalidating poll id and trying resubscribe next time..."
                )
                return False
            else:
                raise json_rpc_error

    def _maybe_unsubscribe(self):
        if self._poll_id is not None:
            self.api.long_polling_unsubscribe(self._poll_id)
            logger.debug(f"Unsubscribed from long poll w/ poll id {self._poll_id}")
            self._poll_id = None

    def _process_long_polling_poll_result(self, raw_result):
        logger.debug(f"Long poll: {raw_result}")
        if raw_result["@type"] == "DeviceServiceData":
            device_id = raw_result["deviceId"]
            if device_id in self._devices_by_id.keys():
                device = self._devices_by_id[device_id]
                device.process_long_polling_poll_result(raw_result)
            else:
                logger.debug(
                    f"Skipping polling result with unknown device id {device_id}."
                )
            return
        if raw_result["@type"] == "message":
            assert "arguments" in raw_result
            if "deviceServiceDataModel" in raw_result["arguments"]:
                raw_data_model = json.loads(
                    raw_result["arguments"]["deviceServiceDataModel"]
                )
                self._process_long_polling_poll_result(raw_data_model)
            else:
                # callback is missing when receiving new message
                message_id = raw_result["id"]
                message = SHCMessage(api=self._api, raw_message=raw_result)
                self._messages_by_id[message_id] = message
            return
        if raw_result["@type"] == "scenarioTriggered":
            if raw_result["id"] in self._scenario_callbacks:
                self._scenario_callbacks[raw_result["id"]](raw_result)
            if (
                "shc" in self._scenario_callbacks
            ):  # deprecated for providing bosch_shc.event trigger callbacks
                self._scenario_callbacks["shc"](raw_result)
            return
        if raw_result["@type"] == "device":
            device_id = raw_result["id"]
            if device_id in self._devices_by_id.keys():
                self._update_device(raw_result)
                if (
                    "deleted" in raw_result and raw_result["deleted"] == True
                ):  # Device deleted
                    logger.debug("Deleting device with id %s", device_id)
                    self._services_by_device_id.pop(device_id, None)
                    self._devices_by_id.pop(device_id, None)
            else:  # New device registered
                logger.debug("Found new device with id %s", device_id)
                device = self._add_device(raw_result, update_services=True)
                for instance, callback in self._subscribers:
                    if isinstance(device, instance):
                        callback(device)
            return
        if raw_result["@type"] in SHCIntrusionSystem.DOMAIN_STATES:
            if self.intrusion_system is not None:
                self.intrusion_system.process_long_polling_poll_result(raw_result)
            return
        if raw_result["@type"] == "userDefinedState":
            state_id = raw_result["id"]
            if state_id in self._userdefinedstates_by_id:
                self._userdefinedstates_by_id[state_id].update_raw_information(
                    raw_result
                )
            else:
                userdefinedstate = SHCUserDefinedState(
                    api=self._api, info=self.information, raw_state=raw_result
                )
                self._userdefinedstates_by_id[state_id] = userdefinedstate
                for instance, callback in self._subscribers:
                    if isinstance(userdefinedstate, instance):
                        callback(userdefinedstate)
            if state_id in self._userdefinedstate_callbacks:
                for callback in self._userdefinedstate_callbacks[state_id]:
                    callback()
            return
        if raw_result["@type"] == "link":
            link_id = raw_result["id"]
            if link_id == "com.bosch.tt.emma.applink":
                self._emma.update_emma_data(raw_result)
        return

    def start_polling(self):
        if self._polling_thread is None:

            def polling_thread_main():
                while not self._stop_polling_thread:
                    try:
                        if not self._long_poll():
                            logger.warning(
                                "_long_poll returned False. Waiting 1 second."
                            )
                            time.sleep(1.0)
                    except RuntimeError as err:
                        self._stop_polling_thread = True
                        logger.info(
                            "Stopping polling thread after expected runtime error."
                        )
                        logger.info(f"Error description: {err}. {err.args}")
                        logger.info(f"Attempting unsubscribe...")
                        try:
                            self._maybe_unsubscribe()
                        except Exception as ex:
                            logger.info(f"Unsubscribe not successful: {ex}")

                    except Exception as ex:
                        logger.error(
                            f"Error in polling thread: {ex}. Waiting 15 seconds."
                        )
                        time.sleep(15.0)

            self._polling_thread = threading.Thread(
                target=polling_thread_main, name="SHCPollingThread"
            )
            self._polling_thread.start()

        else:
            raise SHCSessionError("Already polling!")

    def stop_polling(self):
        if self._polling_thread is not None:
            logger.debug(f"Unsubscribing from long poll")
            self._stop_polling_thread = True
            self._polling_thread.join()

            self._maybe_unsubscribe()
            self._polling_thread = None
            self._poll_id = None
        else:
            raise SHCSessionError("Not polling!")

    def subscribe(self, callback_tuple) -> Callable:
        self._subscribers.append(callback_tuple)

    def subscribe_scenario_callback(self, scenario_id, callback) -> Callable:
        self._scenario_callbacks[scenario_id] = callback

    def unsubscribe_scenario_callback(self, scenario_id) -> Callable:
        self._scenario_callbacks.pop(scenario_id, None)

    def subscribe_userdefinedstate_callback(
        self, userdefinedstate_id, callback
    ) -> Callable:
        self._userdefinedstate_callbacks[userdefinedstate_id].append(callback)

    def unsubscribe_userdefinedstate_callbacks(self, userdefinedstate_id) -> Callable:
        self._userdefinedstate_callbacks.pop(userdefinedstate_id)

    @property
    def devices(self) -> typing.Sequence[SHCDevice]:
        return list(self._devices_by_id.values())

    def device(self, device_id) -> SHCDevice:
        return self._devices_by_id[device_id]

    @property
    def rooms(self) -> typing.Sequence[SHCRoom]:
        return list(self._rooms_by_id.values())

    def room(self, room_id) -> SHCRoom:
        if room_id is not None:
            return self._rooms_by_id[room_id]

        return SHCRoom(self.api, {"id": "n/a", "name": "n/a", "iconId": "0"})

    @property
    def scenarios(self) -> typing.Sequence[SHCScenario]:
        return list(self._scenarios_by_id.values())

    @property
    def scenario_names(self) -> typing.Sequence[str]:
        scenario_names = []
        for scenario in self.scenarios:
            scenario_names.append(scenario.name)
        return scenario_names

    def scenario(self, scenario_id) -> SHCScenario:
        return self._scenarios_by_id[scenario_id]

    @property
    def messages(self) -> typing.Sequence[SHCMessage]:
        return list(self._messages_by_id.values())

    @property
    def emma(self) -> SHCEmma:
        return self._emma

    @property
    def userdefinedstates(self) -> typing.Sequence[SHCUserDefinedState]:
        return list(self._userdefinedstates_by_id.values())

    def userdefinedstate(self, userdefinedstate_id) -> SHCUserDefinedState:
        return self._userdefinedstates_by_id[userdefinedstate_id]

    def authenticate(self):
        self._shc_information = SHCInformation(api=self._api, zeroconf=self._zeroconf)

    def mdns_info(self) -> SHCInformation:
        return SHCInformation(
            api=self._api, authenticate=False, zeroconf=self._zeroconf
        )

    @property
    def information(self) -> SHCInformation:
        return self._shc_information

    @property
    def intrusion_system(self) -> SHCIntrusionSystem:
        return self._domains_by_id["IDS"]

    @property
    def api(self):
        return self._api

    @property
    def device_helper(self) -> SHCDeviceHelper:
        return self._device_helper

    @property
    def rawscan_commands(self):
        return [
            "devices",
            "device",
            "services",
            "device_services",
            "device_service",
            "rooms",
            "scenarios",
            "messages",
            "info",
            "information",
            "public_information",
            "intrusion_detection",
        ]

    def rawscan(self, **kwargs):
        match (kwargs["command"].lower()):
            case "devices":
                return self._api.get_devices()

            case "device":
                return self._api.get_device(device_id=kwargs["device_id"])

            case "services":
                return self._api.get_services()

            case "device_services":
                return self._api.get_device_services(device_id=kwargs["device_id"])

            case "device_service":
                return self._api.get_device_service(
                    device_id=kwargs["device_id"], service_id=kwargs["service_id"]
                )

            case "rooms":
                return self._api.get_rooms()

            case "scenarios":
                return self._api.get_scenarios()

            case "messages":
                return self._api.get_messages()

            case "info" | "information":
                return self._api.get_information()

            case "public_information":
                return self._api.get_public_information()

            case "intrusion_detection":
                return self._api.get_domain_intrusion_detection()

            case _:
                return None
