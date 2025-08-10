from __future__ import annotations

import asyncio
import logging
from abc import ABC
from asyncio import Lock, TimerHandle, Transport, get_running_loop
from collections.abc import Callable
from dataclasses import dataclass

import async_timeout

from . import DeviceData
from .api import RoborockClient
from .exceptions import RoborockConnectionException, RoborockException
from .protocol import Decoder, Encoder, create_local_decoder, create_local_encoder
from .roborock_message import RoborockMessage, RoborockMessageProtocol

_LOGGER = logging.getLogger(__name__)


@dataclass
class _LocalProtocol(asyncio.Protocol):
    """Callbacks for the Roborock local client transport."""

    messages_cb: Callable[[bytes], None]
    connection_lost_cb: Callable[[Exception | None], None]

    def data_received(self, bytes) -> None:
        """Called when data is received from the transport."""
        self.messages_cb(bytes)

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when the transport connection is lost."""
        self.connection_lost_cb(exc)


class RoborockLocalClient(RoborockClient, ABC):
    """Roborock local client base class."""

    def __init__(self, device_data: DeviceData):
        """Initialize the Roborock local client."""
        if device_data.host is None:
            raise RoborockException("Host is required")
        self.host = device_data.host
        self._batch_structs: list[RoborockMessage] = []
        self._executing = False
        self.transport: Transport | None = None
        self._mutex = Lock()
        self.keep_alive_task: TimerHandle | None = None
        RoborockClient.__init__(self, device_data)
        self._local_protocol = _LocalProtocol(self._data_received, self._connection_lost)
        self._encoder: Encoder = create_local_encoder(device_data.device.local_key)
        self._decoder: Decoder = create_local_decoder(device_data.device.local_key)

    def _data_received(self, message):
        """Called when data is received from the transport."""
        parsed_msg = self._decoder(message)
        self.on_message_received(parsed_msg)

    def _connection_lost(self, exc: Exception | None):
        """Called when the transport connection is lost."""
        self._sync_disconnect()
        self.on_connection_lost(exc)

    def is_connected(self):
        return self.transport and self.transport.is_reading()

    async def keep_alive_func(self, _=None):
        try:
            await self.ping()
        except RoborockException:
            pass
        loop = asyncio.get_running_loop()
        self.keep_alive_task = loop.call_later(10, lambda: asyncio.create_task(self.keep_alive_func()))

    async def async_connect(self) -> None:
        should_ping = False
        async with self._mutex:
            try:
                if not self.is_connected():
                    self._sync_disconnect()
                    async with async_timeout.timeout(self.queue_timeout):
                        self._logger.debug(f"Connecting to {self.host}")
                        loop = get_running_loop()
                        self.transport, _ = await loop.create_connection(  # type: ignore
                            lambda: self._local_protocol, self.host, 58867
                        )
                        self._logger.info(f"Connected to {self.host}")
                        should_ping = True
            except BaseException as e:
                raise RoborockConnectionException(f"Failed connecting to {self.host}") from e
        if should_ping:
            await self.hello()
            await self.keep_alive_func()

    def _sync_disconnect(self) -> None:
        loop = asyncio.get_running_loop()
        if self.transport and loop.is_running():
            self._logger.debug(f"Disconnecting from {self.host}")
            self.transport.close()
        if self.keep_alive_task:
            self.keep_alive_task.cancel()

    async def async_disconnect(self) -> None:
        async with self._mutex:
            self._sync_disconnect()

    async def hello(self):
        request_id = 1
        protocol = RoborockMessageProtocol.HELLO_REQUEST
        try:
            return await self.send_message(
                RoborockMessage(
                    protocol=protocol,
                    seq=request_id,
                    random=22,
                )
            )
        except Exception as e:
            self._logger.error(e)

    async def ping(self) -> None:
        request_id = 2
        protocol = RoborockMessageProtocol.PING_REQUEST
        return await self.send_message(
            RoborockMessage(
                protocol=protocol,
                seq=request_id,
                random=23,
            )
        )

    def _send_msg_raw(self, data: bytes):
        try:
            if not self.transport:
                raise RoborockException("Can not send message without connection")
            self.transport.write(data)
        except Exception as e:
            raise RoborockException(e) from e
