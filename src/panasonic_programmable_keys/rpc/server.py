from pathlib import Path
from typing import Iterator

import rpyc
from rpyc.utils.server import ThreadedServer

from ..input import yield_from
from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings


@rpyc.service
class KeyService(rpyc.Service):
    def __init__(self, device_path: Path | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.key_iterator: Iterator[KeyPressEvent] = yield_from(device_path)

    def on_connect(self, conn) -> None:
        logger.info(f"Client connected: {conn}")

    def on_disconnect(self, conn) -> None:
        logger.info(f"Client disconnected: {conn}")

    @rpyc.exposed
    def yield_keys(self) -> Iterator[KeyPressEvent]:
        logger.debug("Reading keys")
        for key_event in self.key_iterator:
            logger.debug(key_event)
            yield key_event

    def get_server(self) -> ThreadedServer:
        port = settings.rpc.get("port", 10018)
        return ThreadedServer(
            self, hostname="127.0.0.1", port=port, logger=logger, protocol_config={"import_custom_exceptions": True}
        )
