"""ZCC Controller Class."""

# flake8: noqa: E501

from __future__ import annotations

import asyncio
import logging
import socket
import time
import uuid
from pprint import pformat
from typing import Dict, List

from zcc.constants import LEVEL_BY_VERBOSITY, NAME, VERSION
from zcc.description import ControlPointDescription
from zcc.device import ControlPointDevice
from zcc.errors import ControlPointError
from zcc.manufacture_info import ControlPointManufactureInfo
from zcc.protocol import ControlPointProtocol
from zcc.socket import ControlPointSocket
from zcc.watchdog import ControlPointWatchdog


class ControlPoint:
    """Represents the ZCC controller which connects to individual devices"""

    def __init__(
        self,
        description: ControlPointDescription = None,
        timeout: int = 2,
        verbosity: int = 0,
    ):
        self.logger = logging.getLogger("ControlPoint")
        if verbosity > 2:
            verbosity = 2
        self.logger.setLevel(LEVEL_BY_VERBOSITY[verbosity])

        self.host = description.host
        self.port = description.port

        self.logger.info("Setting up %s version %s", NAME, VERSION)

        if not (self.host and self.port):
            raise ControlPointError(
                "Initialisation failed - must provide at least host and port."
            )

        self.brand = description.brand
        self.product = description.product
        self.mac = description.mac
        self.available_tcps = description.available_tcps
        self.api_version = description.api_version
        self.firmware_version = description.firmware_version
        self.num_devices = None
        self.num_control_points = None
        self.network_name = None
        self.uptime = None

        self.timeout = timeout
        self.verbosity = verbosity

        self.devices: Dict[ControlPointDevice] = {}
        self.manufacture_infos: Dict[ControlPointManufactureInfo] = {}

        self.actions_received = 0
        self.manufacture_info_received = 0
        self.properties_received = 0
        self.states_received = 0

        self.device_mac = format(uuid.getnode(), "=012x")
        self.access_token = None
        self.session_authorised = False
        self.session_started = False

        self.socket = None
        self.closed_socket = None

        self.ready = False

        self.loop = asyncio.get_event_loop()
        self.session_authorised: asyncio.Future = None
        self.session_started: asyncio.Future = None
        self.gateway_ready: asyncio.Future = None
        self.manufacture_info_ready: asyncio.Future = None
        self.properties_ready: asyncio.Future = None
        self.actions_ready: asyncio.Future = None
        self.states_ready: asyncio.Future = None

        self.connected = asyncio.Event()
        self.connecting = asyncio.Event()

        self.watchdog_timer: ControlPointWatchdog = None

    @property
    def blinds(self) -> List[ControlPointDevice]:
        """Return an array with all blinds"""
        return list(
            filter(lambda device: device.type == "blind", self.devices.values())
        )

    @property
    def doors(self) -> List[ControlPointDevice]:
        """Return an array with all doors"""
        return list(
            filter(lambda device: device.type == "garagedoor", self.devices.values())
        )

    @property
    def fans(self) -> List[ControlPointDevice]:
        """Return an array with all fans"""
        return list(filter(lambda device: device.type == "fan", self.devices.values()))

    @property
    def lights(self) -> List[ControlPointDevice]:
        """Return an array with all lights (i.e. switch or dimmer type)"""
        return list(
            filter(
                lambda device: device.type == "light" or device.type == "dimmer",
                self.devices.values(),
            )
        )

    @property
    def outlets(self) -> List[ControlPointDevice]:
        """Return an array with all outlets"""
        return list(
            filter(
                lambda device: device.type == "outlet" or device.type == "switch",
                self.devices.values(),
            )
        )

    @property
    def sensors(self) -> List[ControlPointDevice]:
        """Return an array with all sensors"""
        return list(
            filter(lambda device: device.type == "garagedoor", self.devices.values())
        )

    async def connect(self, fast: bool = False) -> bool:
        """Connect to ZCC, build device table and subscribe to updates"""
        self.logger.info("Connecting to ZCC %s:%d", self.host, self.port)

        self.connecting.set()
        self.connected.clear()

        if self.session_authorised:
            self.session_authorised.cancel()
        self.session_authorised = self.loop.create_future()

        if self.session_started:
            self.session_started.cancel()
        self.session_started = self.loop.create_future()

        if not self.socket:
            self.socket = ControlPointSocket(
                self.host, self.port, timeout=self.timeout, verbosity=self.verbosity
            )

        try:
            await self.socket.connect()
        except ConnectionRefusedError as error:
            self.connecting.clear()
            description = (
                f"Connection refused when connecting to ZCC {self.host}:{self.port}"
            )
            self.disconnect()
            self.logger.error(description)
            raise ControlPointError(description) from error
        except socket.error as error:
            self.connecting.clear()
            description = f"Socket error when connecting to ZCC {self.host}:{self.port}"
            self.logger.error(description)
            self.disconnect()
            raise ControlPointError(description) from error
        except asyncio.CancelledError as error:
            self.connecting.clear()
            description = (
                f"Cancelled error when connecting to ZCC {self.host}:{self.port}"
            )
            self.logger.error(description)
            self.disconnect()
            raise ControlPointError(description) from error
        except Exception as error:
            self.connecting.clear()
            self.logger.error(error)
            self.disconnect()
            raise ControlPointError("Unknown error when connecting to ZCC") from error

        self.socket.subscribe(self)

        await self.socket.sendall(
            ControlPointProtocol.authorise(self.device_mac), response_expected=False
        )

        try:
            self.logger.debug("Waiting for authorisation")
            await asyncio.wait_for(
                self.session_authorised, timeout=ControlPointProtocol.AUTH_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as error:
            description = f"Unable to authorise session to ZCC {self.host}:{self.port}"
            self.logger.error(description)
            self.disconnect()
            raise ControlPointError(description) from error

        await self.socket.sendall(
            ControlPointProtocol.start(self.device_mac, self.access_token),
            response_expected=False,
        )

        try:
            self.logger.debug("Waiting for session start")
            await asyncio.wait_for(
                self.session_started, timeout=ControlPointProtocol.START_SESSION_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as error:
            description = f"Unable to start session to ZCC {self.host}:{self.port}"
            self.logger.error(description)
            self.disconnect()
            raise ControlPointError(description) from error

        self.gateway_ready = self.loop.create_future()

        await self.socket.sendall(ControlPointProtocol.inforequest())

        try:
            self.logger.debug("Waiting for gateway properties")
            await asyncio.wait_for(
                self.gateway_ready, timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as _:
            description = (
                f"Unable to get gateway properties to ZCC {self.host}:{self.port}"
            )
            self.logger.error(description)

        if not fast:
            await self.__get_control_points()

        await self.socket.sendall(
            ControlPointProtocol.subscribe(), response_expected=False
        )

        await asyncio.sleep(ControlPointProtocol.SUBSCRIBE_TIMEOUT)

        self.ready = True

        self.connected.set()
        self.connecting.clear()

        self.logger.info(
            "Connected to ZCC %s:%d with %d/%d/%d actions/properties/states",
            self.host,
            self.port,
            self.actions_received,
            self.states_received,
            self.properties_received,
        )

    def __del__(self):
        self.disconnect()

    def describe(self) -> str:
        """Return a string representation of ZCC including devices"""
        header = "+" + "-" * 130 + "+"
        if self.host:
            description = header + "\n"
            description += (
                "| Device mac:   %35s          Brand:       %8s              Product:            %8s       |\n"
                % (
                    self.mac if self.mac else "n/a",
                    self.brand if self.brand else "n/a",
                    self.product if self.product else "n/a",
                )
            )
            description += (
                "| Host:         %35s          Port:        %8d              API:                %8s       |\n"
                % (
                    self.host if self.host else "n/a",
                    self.port if self.port else "n/a",
                    self.api_version if self.api_version else "n/a",
                )
            )
            description += (
                "| Firmware:     %35s          Num Devices: %8s              Num Control Points: %8s       |\n"
                % (
                    self.firmware_version if self.firmware_version else "n/a",
                    self.num_devices if self.num_devices else "n/a",
                    self.num_control_points if self.num_control_points else "n/a",
                )
            )
            description += (
                "| Network Name: %35s          Uptime:     %8ss              Tcps:               %8s       |\n"
                % (
                    self.network_name if self.network_name else "n/a",
                    self.uptime if self.uptime else "n/a",
                    str(self.available_tcps) if self.available_tcps else "n/a",
                )
            )
            description += header + "\n"
            description_details = []
            for key in self.manufacture_infos:
                description_details.append(self.manufacture_infos[key].describe())
            for key in self.devices:
                description_details.append(self.devices[key].describe())
            description_details.sort()
            description += "".join(description_details)

            return description
        else:
            return "ControlPoint: not found"

    def disconnect(self):
        """Disconnect from zimi controller"""
        self.ready = False
        if self.socket:
            self.socket.close()
            self.socket = None

    async def __get_control_points(self):
        """Get initial control point data from controller."""

        self.manufacture_info_ready = self.loop.create_future()
        self.manufacture_info_received = 0
        self.properties_ready = self.loop.create_future()
        self.properties_received = 0
        self.actions_ready = self.loop.create_future()
        self.actions_received = 0
        self.states_ready = self.loop.create_future()
        self.states_received = 0

        self.logger.debug("Getting manufacture_info")
        await self.socket.sendall(
            ControlPointProtocol.get("manufacture_info"), response_expected=False
        )

        try:
            await asyncio.wait_for(
                self.manufacture_info_ready,
                timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT,
            )
        except asyncio.exceptions.TimeoutError as error:
            raise ControlPointError(
                "ZCC connection failed - didn't receive manufacture_info."
            ) from error

        await asyncio.sleep(ControlPointProtocol.STEP_TIMEOUT)

        self.logger.debug("Getting initial device properties")
        await self.socket.sendall(
            ControlPointProtocol.get("properties"), response_expected=False
        )

        try:
            await asyncio.wait_for(
                self.properties_ready, timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as error:
            raise ControlPointError(
                "ZCC connection failed - didn't receive any properties."
            ) from error

        await asyncio.sleep(ControlPointProtocol.STEP_TIMEOUT)

        self.logger.debug("Getting initial device actions")
        await self.socket.sendall(
            ControlPointProtocol.get("actions"), response_expected=False
        )

        try:
            await asyncio.wait_for(
                self.actions_ready, timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as error:
            raise ControlPointError(
                "ZCC connection failed - didn't receive any actions."
            ) from error

        await asyncio.sleep(ControlPointProtocol.STEP_TIMEOUT)

        self.logger.debug("Getting initial device states")
        await self.socket.sendall(
            ControlPointProtocol.get("states"), response_expected=False
        )

        try:
            await asyncio.wait_for(
                self.states_ready, timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT
            )
        except asyncio.exceptions.TimeoutError as error:
            raise ControlPointError(
                "ZCC connection failed - didn't receive any states."
            ) from error

        await asyncio.sleep(ControlPointProtocol.STEP_TIMEOUT)

        for key in self.devices.keys():
            identifier_msb = self.devices[key].identifier.split("_")[0]
            if self.manufacture_infos[identifier_msb]:
                self.devices[key].manufacture_info = self.manufacture_infos[
                    identifier_msb
                ]

    async def __get_states(self):
        """Get latest state data from controller and reset watchdog."""

        self.states_ready = self.loop.create_future()

        self.logger.debug("Refreshing device states")
        await self.socket.sendall(ControlPointProtocol.get("states"))

        try:
            await asyncio.wait_for(
                self.states_ready, timeout=ControlPointProtocol.DEVICE_GET_TIMEOUT
            )
            if self.watchdog_timer:
                self.watchdog_timer.reset()
        except asyncio.exceptions.TimeoutError as error:
            self.logger.error(
                "Unable to refresh connection to ZCC - will re-connect: %s\n", error
            )
            await self.re_connect()

    def print_description(self):
        """Print description of the ZCC controller."""
        print(self.describe())

    async def notify(self, notifier):
        """Receive a notification of an updated object.
        Pull the data off the queue.   If None is received then
        assume the socket has been closed and needs re-opening."""

        response = notifier.get()

        if not response:
            if self.ready:
                await self.re_connect()
            return

        self.logger.debug("notify() received:\n%s", response)

        if response.get(ControlPointProtocol.AUTH_APP_FAILED, None):
            self.logger.error("Authorisation failed\n%s", pformat(response))
        if response.get(ControlPointProtocol.AUTH_APP_SUCCESS, None):
            self.logger.debug("Authorisation success\n%s", pformat(response))
            self.access_token = response[ControlPointProtocol.AUTH_APP_SUCCESS][
                "accessToken"
            ]
            self.session_authorised.set_result(True)
        if response.get(ControlPointProtocol.START_SESSION_FAILED, None):
            self.logger.error("Start session failed\n%s", pformat(response))
        if response.get(ControlPointProtocol.START_SESSION_SUCCESS, None):
            self.logger.debug("Start session success\n%s", pformat(response))
            self.session_started.set_result(True)
        if response.get(ControlPointProtocol.CONTROLPOINT_ACTIONS, None):
            self.__update_control_points(
                response.get(ControlPointProtocol.CONTROLPOINT_ACTIONS, None), "actions"
            )
        if response.get(ControlPointProtocol.CONTROLPOINT_PROPERTIES, None):
            self.__update_control_points(
                response.get(ControlPointProtocol.CONTROLPOINT_PROPERTIES, None),
                "properties",
            )
        if response.get(ControlPointProtocol.CONTROLPOINT_MANUFACTURE_INFO, None):
            self.__update_manufacture_info(
                response.get(ControlPointProtocol.CONTROLPOINT_MANUFACTURE_INFO, None)
            )
        if response.get(ControlPointProtocol.CONTROLPOINT_STATES, None):
            self.__update_control_points(
                response.get(ControlPointProtocol.CONTROLPOINT_STATES, None), "states"
            )
        if response.get(ControlPointProtocol.CONTROLPOINT_STATES_EVENTS, None):
            self.__update_control_points(
                response.get(ControlPointProtocol.CONTROLPOINT_STATES_EVENTS, None),
                "states",
            )
        if response.get(ControlPointProtocol.GATEWAY_PROPERTIES, None):
            self.gateway_ready.set_result(True)
            self.__update_properties(
                response.get(ControlPointProtocol.GATEWAY_PROPERTIES, None)
            )
        if response.get(ControlPointProtocol.ZCC_STATUS, None):
            self.logger.error("ZCC status message\n%s", pformat(response))
            await self.re_connect(reset=True)

    async def re_connect(self, reset: bool = False):
        """Re-connect to a new socket and resend any queued messages."""

        if reset:
            self.logger.error(
                "Preparing re-connect to new socket after ZCC intiated reset"
            )
        else:
            self.logger.error(
                "Preparing re-connect to new socket as existing socket closed"
            )

        if self.watchdog_timer:
            self.logger.debug("Pausing existing watchdog timer during re-connection")
            self.watchdog_timer.pause()

        self.socket.unsubscribe(self)
        self.socket.close()

        self.closed_socket = self.socket

        self.ready = False

        while not self.ready:
            self.socket = None

            try:
                self.logger.debug("Re-connecting to ZCC with new socket")
                await self.connect(fast=True)

                while True:
                    message = self.closed_socket.unsent()
                    if message:
                        self.logger.debug("Re-sending message:\n%s", message)
                        await self.socket.sendall(message)
                    else:
                        break
                self.closed_socket = None
            except ControlPointError as error:
                self.logger.error(
                    "Unable to re-connect to ZCC failed with ControlPointError: %s - will retry in %d",
                    error,
                    ControlPointProtocol.RETRY_TIMEOUT,
                )
                await asyncio.sleep(ControlPointProtocol.RETRY_TIMEOUT)

        if self.watchdog_timer:
            self.logger.debug("Re-starting existing watchdog timer after re-connection")
            self.watchdog_timer.reset()

    async def set(self, identifier: str, action: str, params: object = None):
        """Sends an action for a device."""

        while self.connecting.is_set():
            self.logger.error(
                "Controller not ready to accept commands - in process of re-connect"
            )
            await asyncio.sleep(1)

        while not self.connected.is_set():
            self.logger.error(
                "Controller not ready to accept commands - attempting to re-connect"
            )
            try:
                await self.re_connect()
            except ControlPointError as error:
                self.logger.error(
                    "Unable to re-connect to ZCC failed with ControlPointError: %s - will retry",
                    error,
                )

        message = ControlPointProtocol.set(identifier, action, params)
        success = False
        while not success:
            success = await self.socket.sendall(message)
            self.logger.debug(
                "Sending %s request to %s (%s)",
                action,
                self.devices[identifier].location,
                identifier,
            )

    def __str__(self):
        return pformat(vars(self)) + "\n"

    def start_watchdog(self, timer: int = 1800):
        """Start a periodic timeout that resets every time a status update is received."""

        if self.watchdog_timer:
            self.stop_watchdog()

        self.logger.debug("Starting Watchdog for %s seconds", timer)
        self.watchdog_timer = ControlPointWatchdog(timer, self.trigger_watchdog)
        self.watchdog_timer.start()

    def stop_watchdog(self):
        """Stop the periodic timeout."""

        self.logger.debug("Stopping existing Watchdog")

        if self.watchdog_timer:
            self.watchdog_timer.cancel()
            self.watchdog_timer = None

    async def trigger_watchdog(self):
        """Trigger the watchdog function - which will reset the connection."""

        self.logger.debug(
            "Triggering the watchdog timer - will fetch new states to refresh connection"
        )
        await self.__get_states()

    def __update_control_points(self, devices, target):
        """Update control point target with JSON data for all devices."""

        for device in devices:
            updates_made = False
            identifier = device["id"]
            if not self.devices.get(identifier):
                self.devices[identifier] = ControlPointDevice(self, identifier)
            if (
                "actions" in target
                and self.devices[identifier].actions != device[target]
            ):
                self.devices[identifier].actions = device[target]
                self.actions_received += 1
                updates_made = True
            if (
                "properties" in target
                and self.devices[identifier].properties != device[target]
            ):
                self.devices[identifier].properties = device[target]
                self.properties_received += 1
                updates_made = True
            if "states" in target and self.devices[identifier].states != device[target]:
                self.devices[identifier].states = device[target]
                self.states_received += 1
                updates_made = True
            if updates_made:
                if self.watchdog_timer:
                    self.watchdog_timer.reset()
                self.logger.debug(
                    "Received %d/%d actions; %d/%d properties; %d/%d states",
                    self.actions_received,
                    self.num_control_points,
                    self.properties_received,
                    self.num_control_points,
                    self.states_received,
                    self.num_control_points,
                )
                self.logger.debug(
                    "Received %s update for %s (%s):\n%s",
                    target,
                    self.devices[identifier].location,
                    identifier,
                    device[target],
                )
                self.devices[identifier].notify_observers()

        if (
            self.actions_received >= self.num_control_points
            and not self.actions_ready.done()
        ):
            self.actions_ready.set_result(True)
        if (
            self.properties_received >= self.num_control_points
            and not self.properties_ready.done()
        ):
            self.properties_ready.set_result(True)
        if (
            self.states_received >= self.num_control_points
            and not self.states_ready.done()
        ):
            self.states_ready.set_result(True)

    def __update_manufacture_info(self, infos):
        """Update manufacture_info target with JSON data for all devices."""

        for info in infos:
            identifier = info.get("id", None)
            elements = info.get("info", None)
            if identifier and elements:
                self.manufacture_info_received += 1
                self.manufacture_infos[identifier] = ControlPointManufactureInfo(
                    identifier=identifier,
                    manufacturer=elements.get("manufacturer", None),
                    model=elements.get("model", None),
                    hwVersion=elements.get("hwVersion", None),
                    firmwareVersion=elements.get("firmwareVersion", None),
                )

                self.logger.debug(
                    "Received %d/%d: %s",
                    self.manufacture_info_received,
                    self.num_devices,
                    self.manufacture_infos[identifier],
                )

        if self.watchdog_timer:
            self.watchdog_timer.reset()
        if (
            self.manufacture_info_received >= self.num_devices
            and not self.manufacture_info_ready.done()
        ):
            self.manufacture_info_ready.set_result(True)

    def __update_properties(self, properties):
        """Updates zcc gateway properties"""

        properties = properties.get("properties")

        if properties:
            self.brand = properties["brand"]
            self.product = properties["product"]
            self.mac = properties["mac"]
            self.available_tcps = properties["availableTcps"]
            if api_version := properties.get("apiVersion"):
                self.api_version = api_version
            if firmware_version := properties.get("firmwareVersion"):
                self.firmware_version = firmware_version
            self.num_devices = properties["numberOfDevices"]
            self.num_control_points = properties["numberOfControlPoints"]
            self.network_name = properties["networkName"]
            self.uptime = int(time.time()) - properties["uptime"]
