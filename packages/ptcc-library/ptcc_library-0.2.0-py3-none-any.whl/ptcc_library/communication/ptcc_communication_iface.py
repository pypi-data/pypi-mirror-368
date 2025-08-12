# Author: Wojciech Szczytko
# Created: 2025-04-25
import time
from typing import Protocol


class CommunicationInterface(Protocol):
    def write(self, data: bytes) -> None: ...

    def read(self, size: int = 1) -> bytes: ...


class ThrottledCommunication(CommunicationInterface):
    """
    Wraps communication to enforce a minimum delay.

    Parameters
    ----------
    interface: CommunicationInterface
        interface to be wrapped.
    min_delay: float = 0.55
        minimum delay that must be enforced before writing next message.
    """
    def __init__(self, interface: CommunicationInterface, min_delay: float = 0.55):
        self.interface = interface
        self.min_delay = min_delay
        self._last_write_time = 0.0

    def write(self, data: bytes) -> None:
        """
        Enforces minimum delay and invokes write method of provided interface.

        Parameters
        ----------
        data: bytes
            data to be written.
        """
        now = time.time()
        elapsed = now - self._last_write_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.interface.write(data)
        self._last_write_time = time.time()

    def read(self, size: int = 1) -> bytes:
        """
        reads n bytes from provided communication interface.

        Parameters
        ----------
        size: int = 1
            number of bytes to be read form communication interface.
        """
        return self.interface.read(size)
