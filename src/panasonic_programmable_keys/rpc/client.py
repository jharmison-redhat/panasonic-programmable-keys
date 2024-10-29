from pathlib import Path
from typing import Any
from typing import Iterator

import Pyro5.api

from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings
from .server import KeyService


class KeyServerProxy(Pyro5.api.Proxy):
    def _pyroValidateHandshake(self, response: Any = True) -> None:
        logger.debug(f"Sending server handshake: {response}")


class KeyClient(object):
    def __init__(self) -> None:
        self.socket = Path(settings.rpc.get("socket", "/run/panasonic/keys.sock"))
        self.proxy: KeyService = KeyServerProxy(f"PYRO:keyservice@./u:{self.socket}")  # type: ignore

    def ping(self) -> bool:
        try:
            logger.info(f"Pinging server at {self.socket}")
            self.proxy.echo(True)
        except Exception:
            return False
        return True

    def yield_keys(self) -> Iterator[KeyPressEvent]:
        logger.debug("Receiving keys")
        for key_event in self.proxy.yield_keys():
            yield KeyPressEvent(**key_event)
