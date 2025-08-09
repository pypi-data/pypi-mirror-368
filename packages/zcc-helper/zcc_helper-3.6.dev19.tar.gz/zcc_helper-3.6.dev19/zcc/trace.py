"""ZCC Trace Class"""

# flake8: noqa: E501

import imp
import logging
import os
import tracemalloc

from zcc.watchdog import ControlPointWatchdog

_logger = logging.getLogger("ControlPointTrace")


def _package_files(package):
    """Yeild files in moddule.
    Ref https://stackoverflow.com/a/36764029"""

    _, pathname, _ = imp.find_module(package)
    for dirpath, _, filenames in os.walk(pathname):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".py":
                yield os.path.join(dirpath, filename)


class ControlPointTrace:
    """A class to show zcc statistics"""

    def __init__(self, timer: int):
        self.logger = logging.getLogger("ControlPointTrace")

        tracemalloc.start()

        self.statistics_timer = ControlPointWatchdog(timer, self.print_statistics)

        self.statistics_timer.start()

    async def print_statistics(self):
        """Print statistics and re-start timer"""
        print("Printing module memory statistics:\n" + self._statistics)
        self.statistics_timer.reset()

    @property
    def _statistics(self) -> str:
        """Return statistics of the ZCC module."""

        snapshot = tracemalloc.take_snapshot()

        filename_filters = []

        for filename in _package_files("zcc"):
            filename_filters.append(
                tracemalloc.Filter(inclusive=True, filename_pattern=filename)
            )

        snapshot = snapshot.filter_traces(filename_filters)

        summary_count = 0
        summary_bytes = 0

        line_details = ""

        for stat in snapshot.statistics("lineno"):
            summary_count += stat.count
            summary_bytes += stat.size
            line_details += str(stat) + "\n"

        summary_line = "Module has %d objects and totalling %d bytes with lines:\n" % (
            summary_count,
            summary_bytes,
        )

        return summary_line + line_details
