"""
Receiver side of Easy UDP.

Provides `UDPReceiver`, capable of receiving numpy arrays, strings and integers
sent by a compatible `UDPSender` instance.
"""

from easy_udp import EasyUDP
from easy_udp import UDPReceiveException, UDPSendException
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
        collect_window_s: float = 0.1,
        max_pending_bytes: int = 10 * 1024 * 1024,
        pending_message_timeout_s: float = 15.0,
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
        # Buffer to accumulate fragments across receive() calls until meta arrives
        self._pending_fragments: list[bytes] = []
        self._pending_start_time: Optional[float] = None
        self._pending_bytes: int = 0
        self._max_pending_bytes: int = int(max_pending_bytes)
        self._pending_message_timeout_s: float = float(pending_message_timeout_s)

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

            # Append fragment to pending buffer
            self._pending_fragments.append(fragment)
            if self._pending_start_time is None:
                self._pending_start_time = time.time()
            self._pending_bytes += len(fragment)

            # Safety: drop stale/oversized pending buffer to prevent memory blowup
            if self._pending_bytes > self._max_pending_bytes:
                self._pending_fragments.clear()
                self._pending_start_time = None
                self._pending_bytes = 0
                return None
            if (
                self._pending_start_time is not None
                and (time.time() - self._pending_start_time)
                > self._pending_message_timeout_s
            ):
                self._pending_fragments.clear()
                self._pending_start_time = None
                self._pending_bytes = 0
                return None

        if dtype is None:
            # No meta yet; keep buffering
            return None

        if not self._pending_fragments:
            # Meta received but no data fragments: consider message incomplete
            # and wait for a subsequent call to collect more data.
            return None

        # Pop buffered fragments for this message and reset buffer
        received_data = self._pending_fragments
        self._pending_fragments = []
        self._pending_start_time = None
        self._pending_bytes = 0

        if dtype.startswith(b"ndarray"):
            # Supports optional 'ndarray::<dtype_str>' meta
            dtype_str: Optional[str] = None
            if dtype.startswith(b"ndarray::"):
                try:
                    dtype_str = dtype.split(b"::", 1)[1].decode("ascii", errors="ignore")
                except Exception:
                    dtype_str = None

            # If sender sent raw bytes (new behavior), try to rebuild from bytes
            # Otherwise fall back to concatenating pickled fragments (legacy)
            try:
                # Try unpickling first fragment; if it fails, assume raw bytes mode
                _ = pickle.loads(received_data[0])
                # Legacy mode: concatenate unpickled fragments
                parts = [pickle.loads(fragment) for fragment in received_data]
                try:
                    array = np.concatenate(parts) if len(parts) > 1 else parts[0]
                except ValueError as exc:
                    raise UDPReceiveException(f"Failed to reconstruct ndarray: {exc}")
                return array
            except Exception:
                # Raw bytes mode
                raw = b"".join(received_data)
                if dtype_str is None:
                    raise UDPReceiveException("Missing ndarray dtype in metadata")
                try:
                    np_dtype = np.dtype(dtype_str)
                except Exception as exc:
                    raise UDPReceiveException(f"Invalid ndarray dtype: {exc}")
                return np.frombuffer(raw, dtype=np_dtype)

        if dtype == b"str":
            return "".join([pickle.loads(fragment) for fragment in received_data])

        if dtype == b"int":
            return pickle.loads(received_data[0])

        if dtype == b"object":
            # Each fragment is a pickled bytes chunk; unpickle, join, then unpickle the full object
            try:
                byte_chunks = [pickle.loads(fragment) for fragment in received_data]
                data = b"".join(byte_chunks)
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
