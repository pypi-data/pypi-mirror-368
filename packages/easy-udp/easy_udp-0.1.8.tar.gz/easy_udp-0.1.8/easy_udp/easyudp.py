"""
Core primitives for UDP communication.

Exposes an abstract base class `EasyUDP` that owns a UDP socket and provides
common lifecycle helpers. Concrete implementations should implement `send`
and `receive`.
"""

import socket
from abc import ABC, abstractmethod
from typing import Any


class EasyUDP(ABC):
    def __init__(self) -> None:
        """Initialize a new UDP socket and set sane defaults."""

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Allow quick rebinds after restarts
        try:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError:
            # Not critical on some platforms
            pass

        self.socket = udp_socket

    @abstractmethod
    def send(self, message: Any) -> None:
        """Send a message over UDP."""
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> Any:
        """Receive a message over UDP."""
        raise NotImplementedError

    # Lifecycle helpers
    def close(self) -> None:
        """Close the underlying UDP socket."""
        try:
            self.socket.close()
        except Exception:
            pass

    def __enter__(self) -> "EasyUDP":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
