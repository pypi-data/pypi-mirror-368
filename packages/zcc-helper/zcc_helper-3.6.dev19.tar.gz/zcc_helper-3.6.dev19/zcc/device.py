"""ControlPointDevice Class."""

# flake8: noqa: E501

from __future__ import annotations

from pprint import pformat

from zcc.errors import ControlPointError
from zcc.manufacture_info import ControlPointManufactureInfo

OPEN_AND_CLOSE_TOLERANCE = 5
OPEN_AND_CLOSE_WORKAROUND = True


class ControlPointDevice:
    """Represents any ControlPointDevice."""

    def __init__(self, controller, identifier: str):
        """Create a new device associated with a controller and identifed by identifier"""
        self.controller = controller
        self.identifier = identifier
        self.manufacture_info: ControlPointManufactureInfo
        self.actions = {}
        self.properties = {}
        self.states = {}

        self._target_percentage = None
        self._observers = []

    def __str__(self):
        return pformat(vars(self))

    async def __action(self, action: str, params: object = None) -> bool:
        try:
            if self.actions["actions"][action]:
                await self.controller.set(self.identifier, action, params=params)
        except Exception as exception_info:
            raise ControlPointError(
                action + " is not supported for " + self.identifier
            ) from exception_info

    @property
    def __actions(self) -> str:
        """Gets a descriptive string of what actions are supported"""
        description = "{ "
        try:
            if self.actions["actions"].get("TurnOn", None):
                description += "TurnOn TurnOff "
            if self.actions["actions"].get("SetBrightness", None):
                description += "SetBrightness "
            if self.actions["actions"].get("OpenDoor", None):
                description += "OpenDoor CloseDoor "
            if self.actions["actions"].get("OpenToPercentage", None):
                description += "OpenToPercentage "
            if self.actions["actions"].get("SetFanSpeed", None):
                description += "SetFanSpeed "
        except KeyError:
            pass
        description += "}"
        if description == "{ }":
            description = ""
        return description

    @property
    def __states(self) -> str:
        """Gets a descriptive string of the device state"""
        description = ""
        try:
            key = list(self.states["controlState"].keys())[0]
            state = self.states["controlState"][key]
            description += "On" if state.get("isOn", False) else "Off"
            brightness = state.get("brightness", None)
            if brightness:
                description += "/" + str(brightness)
            fan_speed = state.get("fanspeed", None)
            if fan_speed:
                description += "/" + str(fan_speed)
        except IndexError:
            pass
        except KeyError:
            pass
        return description

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of an attached sensor."""
        try:
            state = self.states["controlState"]["sensor"]
            return state.get("batterylevel", 0)
        except KeyError:
            return None

    @property
    def brightness(self) -> int | None:
        """Returns brightness from 0 to 100 or None."""
        try:
            key = list(self.states["controlState"].keys())[0]
            state = self.states["controlState"][key]
            brightness = state.get("brightness", None)
            if brightness:
                return brightness
        except KeyError:
            return False

    async def close_door(self):
        """CloseDoor if the action is supported"""
        if OPEN_AND_CLOSE_WORKAROUND:
            await self.open_to_percentage(1)
        else:
            self._target_percentage = 0
            await self.__action("CloseDoor")

    def describe(self) -> str:
        """Returns a description of a device"""
        return "%-40s   %-38.38s %-8.8s %-8s %s\n" % (
            self.identifier,
            self.location,
            self.type,
            self.__states,
            self.__actions,
        )

    @property
    def door_temp(self) -> int | None:
        """Return the external temperature of an attached sensor."""
        try:
            state = self.states["controlState"]["sensor"]
            return state.get("doortemp", 0)
        except KeyError:
            return None

    async def fade(self, brightness, timeperiod):
        """SetBrightness if the action is supported"""
        await self.__action(
            "SetBrightness",
            params={"brightness": int(brightness), "timeperiod": int(timeperiod)},
        )

    @property
    def fanspeed(self) -> int | None:
        """Returns fanspeed from 0 to 7 or None."""
        try:
            key = list(self.states["controlState"].keys())[0]
            state = self.states["controlState"][key]
            fanspeed = state.get("fanspeed", None)
            if fanspeed:
                return fanspeed
        except KeyError:
            return False

    @property
    def garage_temp(self) -> int | None:
        """Return the internal garage temperature of an attached sensor."""
        try:
            state = self.states["controlState"]["sensor"]
            return state.get("garagetemp", 0)
        except KeyError:
            return None

    @property
    def garage_humidity(self) -> int | None:
        """Return the internal garage humidity of an attached sensor."""
        try:
            state = self.states["controlState"]["sensor"]
            return state.get("garagehumidity", 0)
        except KeyError:
            return None

    @property
    def is_closing(self) -> bool:
        """Returns True if door is closing."""
        if abs(self.percentage - self._target_percentage) <= OPEN_AND_CLOSE_TOLERANCE:
            return False
        if self.percentage and self._target_percentage:
            return self.percentage > self._target_percentage and not self.is_closed
        return False

    @property
    def is_closed(self) -> bool:
        """Returns True if door is closed."""

        if self.percentage:
            return self.percentage <= OPEN_AND_CLOSE_TOLERANCE
        return True

    @property
    def is_connected(self) -> bool:
        """Returns True if connected is on.
        When a device has been disconnected from the mesh it show False."""

        try:
            return self.states["isConnected"]
        except KeyError:
            return False

    @property
    def is_off(self) -> bool:
        """Returns True if status is off."""

        return not self.is_on

    @property
    def is_on(self) -> bool:
        """Returns True if status is on."""

        try:
            key = list(self.states["controlState"].keys())[0]
            state = self.states["controlState"][key]
            return state.get("isOn", False)
        except KeyError:
            return False

    @property
    def is_opening(self) -> bool:
        """Returns True if door is opening and is NOT already open."""
        if abs(self.percentage - self._target_percentage) <= OPEN_AND_CLOSE_TOLERANCE:
            return False
        if self.percentage and self._target_percentage:
            return self.percentage < self._target_percentage and not self.is_open
        return False

    @property
    def is_open(self) -> bool:
        """Returns True if door is open."""

        if self.percentage:
            return self.percentage >= 100 - OPEN_AND_CLOSE_TOLERANCE
        return False

    @property
    def location(self) -> str:
        """Gets a descriptive string of the device location"""
        description = self.properties.get("name", "-") + "/"
        description += self.properties.get("roomName", "-")
        return description

    @property
    def device_name(self) -> str:
        """Gets a device name."""
        return self.manufacture_info.name

    @property
    def name(self) -> str:
        """Gets a descriptive string of the device name"""
        return self.properties.get("name", "-")

    def notify_observers(self):
        """Notify all observers that a state change has occurred."""
        for obs in self._observers:
            obs.notify(self)

    async def open_door(self):
        """OpenDoor if the action is supported"""
        if OPEN_AND_CLOSE_WORKAROUND:
            await self.open_to_percentage(99)
        else:
            self._target_percentage = 100
            await self.__action("OpenDoor")

    async def open_to_percentage(self, percentage):
        """OpenToPercentage if the action is supported"""
        if OPEN_AND_CLOSE_WORKAROUND and percentage == 0:
            percentage = 1
        self._target_percentage = percentage
        await self.__action(
            "OpenToPercentage", params={"openpercentage": int(percentage)}
        )

    @property
    def percentage(self) -> int | None:
        """Return the open to percentage"""
        try:
            key = list(self.states["controlState"].keys())[0]
            state = self.states["controlState"][key]
            return state.get("openpercentage", 0)
        except KeyError:
            return None

    def print_description(self):
        """Print device description."""
        print(self.describe())

    @property
    def room(self) -> str:
        """Gets a descriptive string of the device room"""
        return self.properties.get("roomName", "-")

    async def set_brightness(self, brightness):
        """SetBrightness if the action is supported"""
        await self.__action("SetBrightness", params={"brightness": int(brightness)})

    async def set_fanspeed(self, fanspeed):
        """SetFanSpeed if the action is supported"""
        await self.__action("SetFanSpeed", params={"fanspeed": int(fanspeed)})

    def subscribe(self, observer):
        """Subscribe an observer object for state changes.
        Observer object must include notify(self, observable, *args, **kwargs) method."""
        self._observers.append(observer)

    async def turn_on(self):
        """TurnOn the device if the action is supported"""
        await self.__action("TurnOn")

    async def turn_off(self):
        """TurnOff the device if the action is supported"""
        await self.__action("TurnOff")

    @property
    def type(self) -> str:
        """Gets a descriptive string of the device type"""
        return self.properties.get("controlPointType", "-")

    def unsubscribe(self, observer):
        """Unsubscribe an observer object."""
        self._observers.remove(observer)
