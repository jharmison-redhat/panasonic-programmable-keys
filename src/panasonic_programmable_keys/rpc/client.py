from pathlib import Path
from typing import Iterator

import Pyro5.api

from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings
from .server import KeyService


class KeyClient(object):
    def __init__(self) -> None:
        self.socket = Path(settings.rpc.get("socket", "/run/panasonic/keys.sock"))

    def yield_keys(self) -> Iterator[KeyPressEvent]:
        logger.debug("Receiving keys")
        server: KeyService = Pyro5.api.Proxy(f"PYRO:keyservice@./u:{self.socket}")  # type: ignore
        for key_event in server.yield_keys():
            yield KeyPressEvent(**key_event)
