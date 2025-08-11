"""Static methods for the Zimi Controller protocol."""

# flake8: noqa: E501

import json

from .constants import APP_ID, APP_TOKEN


class ControlPointProtocol:
    """Static methods for the Zimi Controller protocol."""

    AUTH_APP_FAILED = "auth_app_failed"
    AUTH_APP_SUCCESS = "auth_app_success"
    AUTH_TIMEOUT = 30
    START_SESSION_FAILED = "start_session_failed"
    START_SESSION_SUCCESS = "start_session_success"
    START_SESSION_TIMEOUT = 30
    DEVICE_GET_TIMEOUT = 10
    CONTROLPOINT_PROPERTIES = "controlpoint_properties"
    CONTROLPOINT_STATES = "controlpoint_states"
    CONTROLPOINT_ACTIONS = "controlpoint_actions"
    CONTROLPOINT_MANUFACTURE_INFO = "controlpoint_manufacture_info"
    CONTROLPOINT_SETACTIONS = "controlpoint_setactions"
    CONTROLPOINT_STATES_EVENTS = "controlpoint_states_events"
    ZCC_STATUS = "zcc_status"

    SUBSCRIBE_TIMEOUT = 2
    GATEWAY_PROPERTIES = "gateway_properties"
    GATEWAY_PROPERTIES_TIMEOUT = 10

    STEP_TIMEOUT = 0

    RETRY_TIMEOUT = 90

    RESET_TIMEOUT = 90

    UDP_SEND_PORT = 5001
    UDP_RECV_PORT = 5002

    @classmethod
    def authorise(cls, device_mac: str) -> str:
        """Returns the authorise message."""

        request = {
            "request": {
                "type": "auth_app",
                "params": {
                    "appId": APP_ID,
                    "appToken": APP_TOKEN,
                    "deviceMac": device_mac,
                },
            }
        }

        return json.dumps(request)

    @classmethod
    def discover(cls) -> str:
        """Return the discover message to be broadcast on LAN."""
        return "ZIMI"

    @classmethod
    def get(cls, target: str) -> str:
        """Returns the get messages assocated with a target"""
        request = {"request": {"path": "api/v1/controlpoint/", "method": "GET"}}
        if target in ("actions", "manufacture_info", "properties", "states"):
            request["request"]["path"] += target
            return json.dumps(request)
        else:
            raise KeyError(
                'Only "actions", "manufacture_info", "properties" and "states" are supported'
            )

    @classmethod
    def set(cls, identifier: str, action: str, params: object) -> str:
        """Returns the set messages assocated with an action"""
        request = {"request": {"path": "api/v1/controlpoint/actions", "method": "POST"}}
        if action in ("TurnOn", "TurnOff", "OpenDoor", "CloseDoor"):
            body = {"actions": [{"id": identifier, "action": action}]}
            request["request"]["body"] = body
        elif (
            action in ("Fade", "OpenToPercentage", "SetBrightness", "SetFanSpeed")
            and params
        ):
            body = {
                "actions": [
                    {"id": identifier, "action": action, "actionParams": params}
                ]
            }
            request["request"]["body"] = body
        else:
            raise KeyError("Combination of input parameters are not supported")
        return json.dumps(request)

    @classmethod
    def start(cls, device_mac: str, access_token: str) -> str:
        """Returns the start session message."""

        request = {
            "request": {
                "type": "start_session",
                "params": {
                    "appId": APP_ID,
                    "deviceMac": device_mac,
                    "accessToken": access_token,
                },
            }
        }

        return json.dumps(request)

    @classmethod
    def subscribe(cls) -> str:
        """Returns the message assocated with state subscribe"""
        request = {
            "request": {
                "path": "api/v1/subscribe/controlpoint/states",
                "method": "POST",
            }
        }
        return json.dumps(request)

    @classmethod
    def unsubscribe(cls) -> str:
        """Returns the message assocated with state subscribe"""
        request = {
            "request": {
                "path": "api/v1/unsubscribe/controlpoint/states",
                "method": "POST",
            }
        }
        return json.dumps(request)

    @classmethod
    def inforequest(cls) -> str:
        """Returns the message assocated with gateway properties request"""
        request = {"request": {"path": "api/v1/gateway/properties", "method": "GET"}}
        return json.dumps(request)
