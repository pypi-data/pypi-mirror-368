#!/usr/bin/env python3
"""Command line parsing for zcc"""

# flake8: noqa: E501

import asyncio
import argparse
import sys


from zcc import (
    ControlPoint,
    ControlPointDescription,
    ControlPointDiscoveryService,
    ControlPointError,
)


def __options(args):
    parser = argparse.ArgumentParser(
        prog="zcc",
        description="""
                                     A command line interface to a ZIMI home controller.

                                     Operates in two basic modes: (a) discovery mode where
                                     the local network is scanned for a ZCC and the details
                                     are printed, or (b) an execute mode where an action is
                                     sent to a device""",
    )

    parser.add_argument(
        "--verbosity",
        action="store",
        type=int,
        default=0,
        help="verbosity level between 0 and 2",
    )

    command_group = parser.add_argument_group("command")

    cxg = command_group.add_mutually_exclusive_group(required=True)
    cxg.add_argument(
        "--discover", action="store_true", help="discover ZCC and print devices"
    )
    cxg.add_argument(
        "--discover-all", action="store_true", help="discover all ZCC devices on LAN"
    )
    cxg.add_argument(
        "--discover-first",
        action="store_true",
        help="discover first ZCC devices on LAN",
    )
    cxg.add_argument(
        "--execute", action="store_true", help="execute an action on a device"
    )
    cxg.add_argument(
        "--test-connection", action="store_true", help="test the connection to a device"
    )

    host_group = parser.add_argument_group("host")
    host_group.add_argument("--host", action="store", help="zcc host name|address")
    host_group.add_argument("--port", action="store", type=int, help="zcc port")
    host_group.add_argument(
        "--timeout", action="store", type=int, default=3, help="zcc timeout value"
    )

    device_group = parser.add_argument_group("device")
    device_group.add_argument("--device", action="store", help="device identifier")
    device_group.add_argument(
        "--action",
        action="store",
        type=str,
        choices=[
            "CloseDoor",
            "OpenDoor",
            "TurnOn",
            "TurnOff",
            "OpenToPercentage",
            "SetBrightness",
            "SetFanSpeed",
        ],
    )
    device_group.add_argument(
        "--value", action="store", help="device action value (for actions that require)"
    )

    return parser.parse_args(args)


async def main(args):
    """Main function."""

    options = __options(args)

    if options.discover_all:
        await ControlPointDiscoveryService(verbosity=options.verbosity).discovers()
        return

    if options.discover_first:
        await ControlPointDiscoveryService(verbosity=options.verbosity).discover()
        return

    if options.test_connection and options.host and options.port:
        result = await ControlPointDiscoveryService(
            verbosity=options.verbosity
        ).validate_connection(host=options.host, port=options.port)
        print(result)
        return

    if options.host and options.port:
        description = ControlPointDescription(host=options.host, port=options.port)
    else:
        description = await ControlPointDiscoveryService(
            verbosity=options.verbosity
        ).discover()

    controller = ControlPoint(description=description, verbosity=options.verbosity)

    await controller.connect()

    if options.discover:
        controller.print_description()

    if options.execute:
        if options.action and options.device:
            device = controller.devices.get(options.device, None)

            if device:
                if "CloseDoor" in options.action:
                    await device.close_door()
                elif "OpenDoor" in options.action:
                    await device.open_door()
                elif "TurnOn" in options.action:
                    await device.turn_on()
                elif "TurnOff" in options.action:
                    await device.turn_off()
                elif "OpenToPercentage" in options.action:
                    if options.value:
                        await device.open_to_percentage(options.value)
                    else:
                        raise ControlPointError("OpenToPercentage requires --value")
                elif "SetBrightness" in options.action:
                    if options.value:
                        await device.set_brightness(options.value)
                    else:
                        raise ControlPointError("SetBrightness requires --value")
                elif "SetFanSpeed" in options.action:
                    if options.value:
                        await device.set_fanspeed(options.value)
                    else:
                        raise ControlPointError("SetFanSpeed requires --value")
                else:
                    raise ControlPointError("No valid --device and --action")
            else:
                raise ControlPointError(f"No device {options.device} exists")
        else:
            raise ControlPointError("--execute needs --device and --action options")

    if controller:
        controller.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main(sys.argv[1:]))
    except ControlPointError as error:
        print(f"zcc {' '.join(sys.argv[1:])}: {error}")
