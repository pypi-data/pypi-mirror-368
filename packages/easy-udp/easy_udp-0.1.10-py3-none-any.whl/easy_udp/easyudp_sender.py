"""
Sender side of Easy UDP.

Provides `UDPSender`, capable of sending numpy arrays, strings and integers.
"""

from easy_udp import EasyUDP
from easy_udp import UDPSendException, UDPTypeException
from numpy import ndarray
import numpy as np
import pickle
from typing import Any, Union


class UDPSender(EasyUDP):
    def __init__(self, host: str, port: int) -> None:
        """
        Initialize a UDPSender instance.

        Args:
            host (str): The host address for the socket connection.
            port (int): The port number for the socket connection.
            Note: UDP is message-oriented; this class fragments large payloads and
            sends a short meta frame afterwards describing the payload type.

        """

        super().__init__()
        self.host = host
        self.port = port

    def _send_metadata(self, message_type: Union[ndarray, str, int, object], dtype_str: str | None = None) -> None:
        """
        Sends metadata based on the message type to the specified host and port.

        Args:
            message_type (Union[ndarray, str, int]): The type of the message to be sent.

        """
        if message_type == ndarray:
            if dtype_str is not None:
                meta = b"Meta::ndarray::" + dtype_str.encode("ascii", errors="ignore")
            else:
                meta = b"Meta::ndarray"
            self.socket.sendto(meta, (self.host, self.port))
        elif message_type == str:
            self.socket.sendto(b"Meta::str", (self.host, self.port))
        elif message_type == int:
            self.socket.sendto(b"Meta::int", (self.host, self.port))
        elif message_type == object:
            self.socket.sendto(b"Meta::object", (self.host, self.port))

    def _send_ndarray(self, message: ndarray) -> None:
        """
        Send a NumPy array as fragments.

        Args:
            message (ndarray): The NumPy array to be sent.

        """

        # Ensure C-contiguous view and compute dtype
        flat: np.ndarray = np.ravel(message)
        dtype_str = np.dtype(flat.dtype).str

        # Send raw bytes of the array in MTU-safe chunks; receiver will rebuild with dtype
        data_bytes: bytes = flat.tobytes(order="C")
        if not data_bytes:
            # Empty array: just send meta with dtype
            self._send_metadata(ndarray, dtype_str)
            return

        # Send raw bytes, not pickled chunks
        self._send_fragments(data_bytes, len(data_bytes), 1, (ndarray, dtype_str), use_pickle=False)

    def _send_integer(self, message: int) -> None:
        """
        Send an integer as a serialized byte stream.

        Args:
            message (int): The integer to be sent.

        """

        number_bytes = pickle.dumps(message)
        if len(number_bytes) > 1400:
            raise UDPSendException("Integer too large; pickled size must be <= ~1400 bytes to avoid UDP fragmentation")

        self.socket.sendto(number_bytes, (self.host, self.port))
        self._send_metadata(int)

    def _send_object(self, message: Any) -> None:
        """
        Send an arbitrary Python object by serializing it with pickle and
        fragmenting the resulting bytes.

        Args:
            message (Any): Arbitrary picklable Python object.
        """

        try:
            data_bytes: bytes = pickle.dumps(message)
        except Exception as exc:
            raise UDPSendException("Failed to serialize object via pickle") from exc

        self._send_fragments(data_bytes, len(data_bytes), 1, object)

    def _send_fragments(self, message: Any, length: int, byte_size: int, dtype, *, use_pickle: bool = True) -> None:
        """
        Send fragments of a message.

        Args:
            message: The message to be sent.
            length: The length of the message.

        """

        # Aim for fragments comfortably below typical UDP MTU (~1500) while
        # allowing large socket buffers. We choose element-count based slicing
        # since arrays/strings are indexed by element, not bytes.
        # For arrays, byte_size is the element size; for strings it's 1.
        max_payload_bytes = 1400
        fragment_size = max(1, max_payload_bytes // max(1, byte_size))
        for i in range(0, length, fragment_size):
            fragment = message[i : i + fragment_size]
            if use_pickle:
                payload = pickle.dumps(fragment)
            else:
                # Ensure bytes payload
                payload = fragment if isinstance(fragment, (bytes, bytearray)) else bytes(fragment)
            self.socket.sendto(payload, (self.host, self.port))

        # Send type metadata after all fragments
        if dtype is ndarray or (isinstance(dtype, tuple) and dtype and dtype[0] is ndarray):
            dtype_str = dtype[1] if isinstance(dtype, tuple) and len(dtype) > 1 else None
            self._send_metadata(ndarray, dtype_str)
        else:
            self._send_metadata(dtype)

    def send(self, message: Any) -> None:
        """
        Send a message through UDP.

        Args:
            message: The message to be sent.

        Raises:
            UDPSendException: If the message type is not supported.

        """

        if isinstance(message, ndarray):
            self._send_ndarray(message)

        elif isinstance(message, str):
            self._send_fragments(message, len(message), 1, str)

        elif isinstance(message, int):
            self._send_integer(message)

        else:
            # Fallback to generic object serialization
            self._send_object(message)

    def receive(self) -> Any:
        """
        Receive method not supported for UDPSender.

        Raises:
            UDPTypeException: If receive method is called on UDPSender.

        """

        raise UDPTypeException(
            "UDPSender does not support receiving messages; use UDPReceiver instead"
        )
