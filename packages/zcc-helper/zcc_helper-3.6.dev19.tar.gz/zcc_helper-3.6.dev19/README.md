# ZCC-HELPER

The ZIMI library is a basic python API and command line tool that supports the zimi Cloud Connect device to manage Powermesh home network equipment.

## Installation

You can install zimi from PyPi:

```
pip install zcc-helper
```

The module is only supported in python3.

## How to use

The module can be used both as part of an embedded python program and as a command line tool.

### Embedded Program

In order to control the zimi Cloud Connect (ZCC) and associated devices your program should create an instance of a ControlPoint object which will be used to manipulate the associated devices.   There is a multi-step process to do so described below.

#### Step One - discover details of the Zimi Controller and create a ControlPointDescription object

If you are connected to the local LAN with the Zimi Controller, then you can auto discover the ZCC otherwise you need to know the IP address and port number of the ZCC.

To discover ZCC and devices on the local LAN use the ControlPointDiscoveryService.discover() async method to obtain a ControlPointDescription object with details of host, port etc as per the code snippet below:

```python
    import asyncio
    from zcc import ControlPoint, ControlPointDescription, ControlPointDiscoveryService


    async def discover():
        return await ControlPointDiscoveryService().discover()


    async def main():
        controller_description = await discover()
        print(controller_description)

    asyncio.run(main())
```

When this is run it produces output like:

```python
ControlPointDescription(brand='zimi', product='zcc', mac='c4ffbc90bf73', host='192.168.1.105', port=5003, available_tcps=6)
```

#### Step Two - Create a ControlPoint object and connect to the controller

Once you have discovered details of the ZIMI controller your program should create a ControlPoint instance and use the async connect() method to authorise and start a session with the ZIMI controller as well as build a catalogue of all associated devices.

Use some code as per the snippet below:

```python
    import asyncio
    from zcc import ControlPoint, ControlPointDescription, ControlPointDiscoveryService


    async def discover():
        return await ControlPointDiscoveryService().discover()


    async def main():
        description = await discover()
        controller = ControlPoint(description=description)
        await controller.connect()
        controller.print_description()

    asyncio.run(main())
```

When this is run it produces output like:

```text
+----------------------------------------------------------------------------------------------------------------------------------+
| ControlPoint: c4ffbc90bf73             zcc     zimi                          59 devices           192.168.1.105:5003   6 Tcps    |
+----------------------------------------------------------------------------------------------------------------------------------+
bddf0500-4d15-4457-b063-c12ed208a0b0_3   Study Pendant/Upstairs                   switch   Off      { TurnOn TurnOff }
bddf0500-4d15-4457-b063-c12ed208a0b0_4   Lounge/Upstairs                          switch   Off      { TurnOn TurnOff }
37bd164e-d867-4ba7-b64c-e7d4c4d0f418_1   Kitchen Downlights/Kitchen               switch   Off      { TurnOn TurnOff }
```

It is also possible to connect to a known ZCC host with ip address and port number wrapped in a ControlPointDescription object:

```python
controller = ControlPoint(description=ControlPointDescription(host='192.168.1.105', port=5003))
```

#### Step Three - Control devices connected to the controller

Once the device ID is known then it can be used to control a particular device by using the controller.devices[device_id] instance that represents an individual device.

```python
>>> dev = zcc.devices['bddf0500-4d15-4457-b063-c12ed208a0b0_3']
>>> print(dev)
{'actions': {'actions': {'TurnOff': {'actionParams': {}},
                         'TurnOn': {'actionParams': {}}}},
 'controller': <zcc.controller.ControlPoint object at 0x7f70a9f117f0>,
 'identifier': 'bddf0500-4d15-4457-b063-c12ed208a0b0_3',
 'properties': {'controlPointType': 'switch',
                'name': 'Study Pendant',
                'roomId': 5,
                'roomName': 'Up Stairs Passage'},
 'states': {'controlState': {'switch': {'isOn': False}}, 'isConnected': True}}
>>> dev.turn_on()
>>> print(dev)
{'actions': {'actions': {'TurnOff': {'actionParams': {}},
                         'TurnOn': {'actionParams': {}}}},
 'controller': <zcc.controller.ControlPoint object at 0x7f70a9f117f0>,
 'identifier': 'bddf0500-4d15-4457-b063-c12ed208a0b0_3',
 'properties': {'controlPointType': 'switch',
                'name': 'Study Pendant',
                'roomId': 5,
                'roomName': 'Up Stairs Passage'},
 'states': {'controlState': {'switch': {'isOn': True}}, 'isConnected': True}}
>>> dev.turn_off()
```

Depending upon the type of device it will support various actions as defined in ControlPointDevice.

Available actions include:

```python
    async def close_door(self):
        '''CloseDoor if the action is supported'''

    async def fade(self, brightness, timeperiod):
        '''SetBrightness if the action is supported'''

    async def open_door(self):
        '''OpenDoor if the action is supported'''

    async def open_to_percentage(self, percentage):
        '''OpenToPercentage if the action is supported'''

    async def set_brightness(self, brightness):
        '''SetBrightness if the action is supported'''

    async def set_fanspeed(self, fanspeed):
        '''SetFanSpeed if the action is supported'''

    async def turn_on(self):
        '''TurnOn the device if the action is supported'''

    async def turn_off(self):
        '''TurnOff the device if the action is supported'''
```

Available properties include:

```python
    def battery_level(self) -> int | None:
        '''Return the battery level of an attached sensor.'''

    def brightness(self) -> int | None:
        '''Returns brightness from 0 to 100 or None.'''

    def door_temp(self) -> int | None:
        '''Return the external temperature of an attached sensor.'''

    def fanspeed(self) -> int | None:
        '''Returns fanspeed from 0 to 7 or None.'''

    def garage_humidity(self) -> int | None:
        '''Return the internal garage humidity of an attached sensor.'''

    def garage_temp(self) -> int | None:
        '''Return the internal garage temperature of an attached sensor.'''

    def is_closing(self) -> bool:
        '''Returns True if door is closing.'''

    def is_closed(self) -> bool:
        '''Returns True if door is closed.'''

    def is_connected(self) -> bool:
        '''Returns True if connected is on.
        When a device has been disconnected from the mesh it show False.'''

    def is_off(self) -> bool:
        '''Returns True if status is off.'''

    def is_on(self) -> bool:
        '''Returns True if status is on.'''

    def is_opening(self) -> bool:
        '''Returns True if door is opening.'''

    def is_open(self) -> bool
        '''Returns True if door is open.'''

    def location(self) -> str:
        '''Gets a descriptive string of the device location'''

    def name(self) -> str:
        '''Gets a descriptive string of the device name'''

    def percentage(self) -> int | None:
        '''Return the open to percentage'''

    def room(self) -> str:
        '''Gets a descriptive string of the device room'''

    def type(self) -> str:
        '''Gets a descriptive string of the device type'''
```

In addition, you can subscribe to a notification for changes to the device state by using the following methods of the device object.

```python
    def subscribe(self, observer):
        '''Subscribe an observer object for state changes.
        Observer object must include notify(self, observable, *args, **kwargs) method.'''

    def unsubscribe(self, observer):
        '''Unsubscribe an observer object.'''
```

The observer object must have a notify(observable) method.

Finally, you can initiate a watchdog function that will periodically refresh the device states from the ZCC.   This can be useful for long lived connections that may time-out as it will trigger a re-connection if needed.

```python
    def start_watchdog(self, timer: int):
        '''Start a periodic timeout that resets every time a status update is received.'''

    def stop_watchdog(self):
        '''Stop the periodic timeout.'''

```
### Command Line Program

ZCC can also be used as a command line tool to discover ZCC devices and/or execute actions upon them.

```
$ python3 -m zcc
usage: zcc [-h] [--verbosity VERBOSITY] (--discover | --execute) [--host HOST] [--port PORT] [--timeout TIMEOUT] [--device DEVICE]
           [--action {CloseDoor,OpenDoor,TurnOn,TurnOff,OpenToPercentage,SetBrightness,SetFanSpeed}] [--value VALUE]
zcc: error: one of the arguments --discover --execute is required
```

To discover devices use:

```
$ python -m zcc --discover
+-----------------------------------------------------------------------------------------------------------------+
| ControlPoint: c4ffbc90bf73             zcc     zimi         34 devices           192.168.1.105:5003   6 Tcps    |
+-----------------------------------------------------------------------------------------------------------------+
0a872922-73e0-4699-89c5-29156f0686f8_1   LED strip/Lounge        dimmer   Off      { TurnOn TurnOff SetBrightness }
0da922e4-1f04-4a80-b267-ade8529194c9_1   Water Feature Pu        switch            { TurnOn TurnOff }
```

To execute an action use:

```
python -m zcc --execute --device 'bddf0500-4d15-4457-b063-c12ed208a0b0_3' --action 'TurnOn'
```

This version of the command is relatively slow as it first of all discovers the ZCC on the local LAN, builds a device inventory and then executes the action.
