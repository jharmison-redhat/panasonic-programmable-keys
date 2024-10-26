from ipaddress import IPv4Address
from typing import Annotated
from typing import Any
from typing import Iterator

import rpyc
from annotated_types import Interval
from pydantic import BaseModel
from pydantic import Strict
from pydantic.networks import IPvAnyAddress

from .server import KeyService
from ..input.models import KeyPressEvent
from ..util import logger
from ..util import settings


class KeyClient(BaseModel):
    address: IPvAnyAddress = IPv4Address("127.0.0.1")
    port: Annotated[int, Strict(True), Interval(gt=0, lt=65536)] = settings.rpc.get("port", 10018)

    def connect(self) -> KeyService:
        logger.debug(f"Creating connection: {self.address}:{self.port}")
        return rpyc.connect(str(self.address), self.port).root

    def yield_keys(self) -> Iterator[KeyPressEvent]:
        logger.debug("Receiving keys")
        yield from self.connect().yield_keys()
