"""ControlPointManufactureInfo Class."""

from dataclasses import dataclass


@dataclass
class ControlPointManufactureInfo:
    """Data class to store ControlPoint manufacture_info."""

    identifier: str = None
    manufacturer: str = None
    model: str = None
    hwVersion: str = None
    firmwareVersion: str = None

    def describe(self) -> str:
        """Returns a description of a device"""
        return "%-40s %-40.40s %-8.8s          %s\n" % (
            self.identifier,
            f"{self.model} ({self.name})",
            "device",
            f"( hw={self.hwVersion}, fw={self.firmwareVersion} )",
        )

    @property
    def name(self) -> str:
        """Returns simplified name of the device."""

        if not self.model:
            return "N/A"

        if "Blind" in self.model:
            return "Cover"
        if "Fan" in self.model:
            return "Fan"
        if "Garage" in self.model:
            return "Garage"
        if "Door" in self.model:
            return "Cover"
        if "GPO" in self.model:
            return "Outlet"
        if "Switch" in self.model:
            return "Switch"

        return self.model
