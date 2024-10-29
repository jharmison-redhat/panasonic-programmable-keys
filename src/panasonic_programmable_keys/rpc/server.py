import os
from pathlib import Path
from typing import Any
from typing import Iterator

import Pyro5.api
from Pyro5.socketutil import SocketConnection

from ..input import InputDevices
from ..input import panasonic_keyboard_device_path
from ..input import yield_from
from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings


class KeyServiceDaemon(Pyro5.api.Daemon):

    def validateHandshake(self, conn: SocketConnection, data: Any) -> Any:
        logger.info(f"Incoming request from {conn.sock} with data: {data}")
        return data

    def clientDisconnect(self, conn: SocketConnection) -> None:
        logger.info(f"Session closed with {conn.sock}")


@Pyro5.api.expose
class KeyService(object):
    def __init__(self, device_path: Path | None = None) -> None:
        self.device_path: Path | None = device_path
        self.devices = InputDevices.load(self.device_path)

    def yield_keys(self) -> Iterator[dict]:
        logger.debug("Reading keys")

        key_event: KeyPressEvent
        for key_event in yield_from(panasonic_keyboard_device_path(devices=self.devices)):
            logger.debug(key_event)
            yield key_event.model_dump()

    def echo(self, data: Any) -> Any:
        logger.debug(f"Received echo request: {data}")
        return data


def get_server(device_path: Path | None = None) -> KeyServiceDaemon:
    socket = Path(settings.rpc.get("socket", "/run/panasonic/keys.sock"))
    if socket.exists():
        socket.unlink()
    socket.parent.mkdir(exist_ok=True)

    server = KeyServiceDaemon(unixsocket=str(socket))
    os.chmod(socket, 0o777)  # ensure that the socket can be read by everyone
    uri = server.register(KeyService(device_path=device_path), objectId="keyservice")
    logger.debug(f"Listening at: {uri}")
    return server
