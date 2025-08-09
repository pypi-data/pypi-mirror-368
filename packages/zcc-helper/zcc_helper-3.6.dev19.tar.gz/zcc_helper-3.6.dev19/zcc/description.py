'''ZCC Zimi Controller Description Class'''
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ControlPointDescription:
    '''Data class to store ControlPoint description.'''

    brand: str = None
    product: str = None
    mac: str = None
    host: str = None
    port: int = None
    available_tcps: int = None
    api_version: str = 'n/a'
    firmware_version: str = 'n/a'
