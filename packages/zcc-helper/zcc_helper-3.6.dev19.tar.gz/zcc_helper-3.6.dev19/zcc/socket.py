"""A socket connection to a Zimi Controller."""

# flake8: noqa: E501

import asyncio
from codecs import StreamReader, StreamWriter
import json
from json.decoder import JSONDecodeError
import logging
import queue
import socket

from zcc.constants import LEVEL_BY_VERBOSITY


class ControlPointSocket:
    """A TCP/IP socket that includes recvall method with timeout"""

    def __init__(self, host: str, port: int, timeout: int = None, verbosity: int = 0):
        """Create new TCP/IP socket to host and port with optional timeout.
        Update objects are made available via a FIFO queue."""

        self.host = host
        self.port = port

        self._observers = []

        self.listen_task: asyncio.Task = None

        self.listen_queu = queue.Queue()
        self.send_queu = queue.Queue()

        self.loop = asyncio.get_event_loop()

        self.logger = logging.getLogger("ControlPointSocket")
        self.logger.setLevel(LEVEL_BY_VERBOSITY[verbosity])

        self.sock: socket.socket = None
        self.reader: StreamReader = None
        self.writer: StreamWriter = None

        self.timeout = timeout

    async def connect(self):
        """Connect to an OS socket and begin listening."""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.sock and self.timeout:
            self.sock.settimeout(self.timeout)

        try:
            self.sock.connect((self.host, self.port))
            self.reader, self.writer = await asyncio.open_connection(sock=self.sock)
            self.listen_task = asyncio.create_task(self.__listen())
        except asyncio.CancelledError as error:
            self.logger.error("Connection cancelled")
            raise error
        except ConnectionRefusedError as error:
            self.logger.error(
                "Connection refused %s error from %s:%s",
                error,
                self.host,
                str(self.port),
            )
            raise error
        except socket.error as error:
            self.logger.error(
                "Connection received socket %s error from %s:%s",
                error,
                self.host,
                str(self.port),
            )
            raise error

    async def __listen(self):
        """Worker thread to monitor state change events and update objects.
        Sends a notify to observers when new items are put in the queue OR the
        underlying socket is closed."""

        while True:
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout=1)
                if line == b"":
                    continue
                response = json.loads(line).get("response")
                if response:
                    self.listen_queu.put(response)
                    for obs in self._observers:
                        await obs.notify(self)
                    self.send_queu.get(block=False)
            except asyncio.CancelledError:
                self.logger.debug("Listening connection cancelled")
                break
            except asyncio.TimeoutError:
                if self.sock and self.sock.fileno() != -1 and self.reader:
                    pass
                else:
                    self.logger.error(
                        "Listening connection socket failure after timeout"
                    )
                    break
            except AttributeError:
                self.logger.error("Listening connection cancelled during timeout")
                break
            except (ConnectionResetError, ConnectionAbortedError) as error:
                self.logger.error("Llstening connection reset error %s", error)
                break
            except JSONDecodeError as error:
                self.logger.error(
                    "Listening connection JSON decode error %s:\n%s", error, line
                )
                break
            except queue.Empty:
                pass

        self.logger.debug("Listening connection socket closed")

        self.listen_task = None  # Remove reference before closing
        self.close()

        for obs in self._observers:
            await obs.notify(self)

    def close(self) -> None:
        """Close socket"""
        if self.listen_task:
            self.listen_task.cancel()
        if self.sock:
            self.sock.close()
        self.reader = None
        self.writer = None
        self.sock = None

    def get(self):
        """Fetch an item from the queue.  Returns None if the queue is empty.
        Notify for an empty queue should have only been sent if the socket has
        been closed and an extra notify() was sent."""

        try:
            response = self.listen_queu.get(block=False)
        except queue.Empty:
            response = None

        return response

    async def sendall(self, message: str, response_expected: bool = True) -> bool:
        """Send all bytes of string to socket end-point.   If the socket is closed
        send a None notify to prompt re-connect.  If response_expected is set
        the message is saved in a queu incase it needs to be retrieved to send again."""

        if response_expected:
            self.send_queu.put(message)

        if (
            self.sock
            and self.sock.fileno() != -1
            and self.writer
            and not self.writer.is_closing()
        ):
            self.logger.debug("sendall()\n%s", message)
            self.writer.write(message.encode())
            await self.writer.drain()
            return True
        else:
            self.logger.error("Send failed with no socket:\n%s", message)
            self.close()
            for obs in self._observers:
                await obs.notify(self)
            return False

    def subscribe(self, observer):
        """Subscribe an observer object for state changes.
        Observer object must include an async notify(self, observable, *args, **kwargs) method."""
        self._observers.append(observer)

    def unsubscribe(self, observer):
        """Unsubscribe an observer object."""
        try:
            self._observers.remove(observer)
        except ValueError as error:
            self.logger.debug(
                "Unsubscribe failed with value error: %s for %s", error, observer
            )

    def unsent(self):
        """Fetch an item from the unsent queue.  Returns None if the queue is empty."""

        try:
            response = self.send_queu.get(block=False)
        except queue.Empty:
            response = None

        return response
