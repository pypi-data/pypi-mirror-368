"""
Receiver side of Easy UDP.

Provides `UDPReceiver`, capable of receiving numpy arrays, strings and integers
sent by a compatible `UDPSender` instance.
"""

from easy_udp import EasyUDP
from easy_udp import UDPReceiveException
import pickle
from typing import Optional, Union
from numpy import ndarray
import socket
import errno
import numpy as np
import time


class UDPReceiver(EasyUDP):
    def __init__(
        self,
        host: str,
        port: int,
        *,
        recv_timeout_s: Optional[float] = None,
        collect_window_s: float = 0.02,
    ) -> None:
        """
        Initialize a UDPReceiver instance.

        Args:
            host (str): The host address for the socket connection.
            port (int): The port number for the socket connection.
            recv_timeout_s (float | None): Optional timeout for receive operations.

        """
        super().__init__()
        self.host = host
        self.port = port
        self.socket.bind((self.host, self.port))
        if recv_timeout_s is not None:
            self.socket.settimeout(recv_timeout_s)
        else:
            # Non-blocking to allow cooperative loops
            self.socket.setblocking(False)
        # Small window to collect fragments in non-blocking mode
        self._collect_window_s = max(0.0, float(collect_window_s))

    def send(self):
        """
        Raise UDPSendException when the UDP Client cannot send.
        """
        raise UDPSendException("UDP Client cannot send")

    def _receive_fragments(self) -> Union[ndarray, str, int, None]:
        """
        Receive fragments from a socket and concatenate them into a single data array.

        Returns:
            Union[ndarray, str, int]: The assembled array if data is received, otherwise returns None.
        """
        received_data: list[bytes] = []
        dtype: Optional[bytes] = None

        # Read until we get meta marker or we time out/non-block
        deadline: Optional[float] = None
        if self.socket.gettimeout() is None:
            deadline = time.time() + self._collect_window_s

        while True:
            try:
                # Maximum UDP payload we expect
                fragment, _addr = self.socket.recvfrom(65535)
            except socket.timeout:
                # No complete message within timeout
                break
            except OSError as e:
                if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                    # No data in non-blocking mode; give it a short window
                    if deadline is None or time.time() >= deadline:
                        break
                    # Tiny sleep to avoid busy spin
                    time.sleep(0.001)
                    continue
                raise

            if fragment.startswith(b"Meta::"):
                dtype = fragment.replace(b"Meta::", b"")
                break

            received_data.append(fragment)

        if not received_data or dtype is None:
            return None

        if dtype == b"ndarray":
            if not received_data:
                return np.array([])
            parts = [pickle.loads(fragment) for fragment in received_data]
            try:
                array = np.concatenate(parts) if len(parts) > 1 else parts[0]
            except ValueError as exc:
                raise UDPReceiveException(f"Failed to reconstruct ndarray: {exc}")
            return array

        if dtype == b"str":
            return "".join([pickle.loads(fragment) for fragment in received_data])

        if dtype == b"int":
            return pickle.loads(received_data[0])

        if dtype == b"object":
            # For objects we fragment raw bytes; concatenate and unpickle
            data = b"".join(received_data)
            try:
                return pickle.loads(data)
            except Exception as exc:
                raise UDPReceiveException(f"Failed to deserialize object: {exc}")

        # Unknown dtype marker
        return None

    def receive(self) -> Union[ndarray, str, int, None]:
        """
        Receive data from the socket.

        Returns:
            Union[ndarray, str, int, None]: The assembled array if data is received, otherwise returns None.
        """
        return self._receive_fragments()
