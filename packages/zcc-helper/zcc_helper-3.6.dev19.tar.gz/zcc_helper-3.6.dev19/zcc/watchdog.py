'''ZCC Watchdog Timer Class'''

import asyncio
import logging


class ControlPointWatchdog:
    '''A class to create a timer with callback.'''

    def __init__(self, timeout: int, callback):

        self.logger = logging.getLogger('ControlPointWatchdog')

        self._busy = False
        self._timeout = timeout
        self._callback = callback
        self._task = None
        self.logger.debug(
            "Created watchdog timer for %d seconds", self._timeout)

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._busy = True
        await self._callback()
        self._busy = False

    def cancel(self):
        '''Cancel the timer.'''
        if not self._busy:
            self._task.cancel()

    def pause(self):
        '''Pause the timer'''
        if self._task:
            self.cancel()

    def reset(self):
        '''Reset the timer.'''
        if self._task:
            self.cancel()
        self.start()

    def start(self):
        '''Start the timer.'''
        self._task = asyncio.ensure_future(self._job())
