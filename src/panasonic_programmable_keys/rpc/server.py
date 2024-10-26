from pathlib import Path
from typing import Iterator

import Pyro5.api

from ..input import InputDevices
from ..input import panasonic_keyboard_device_path
from ..input import yield_from
from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings


@Pyro5.api.expose
class KeyService(object):
    def __init__(self, device_path: Path | None = None) -> None:
        self.device_path: Path | None = device_path

    def yield_keys(self) -> Iterator[dict]:
        logger.debug("Reading keys")
        devices = InputDevices.load(self.device_path)
        for key_event in yield_from(panasonic_keyboard_device_path(devices=devices)):
            logger.debug(key_event)
            yield key_event.model_dump()


def get_server(device_path: Path | None = None) -> Pyro5.api.Daemon:
    socket = Path(settings.rpc.get("socket", "/run/panasonic/keys.sock"))
    if socket.exists():
        socket.unlink()
    socket.parent.mkdir(exist_ok=True)

    server = Pyro5.api.Daemon(unixsocket=str(socket))
    uri = server.register(KeyService(device_path=device_path), objectId="keyservice")
    logger.debug(f"Listening at: {uri}")
    return server
