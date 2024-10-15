from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationInfo
from pydantic import field_validator

from ..util import logger
from ..util import settings

NON_DEVICE_HANDLERS = ["kbd", "sysrq", "leds", "rfkill"]


class InputDeviceId(BaseModel):
    bus: str | int
    vendor: str | int
    product: str | int
    version: str | int

    @field_validator("*")
    @classmethod
    def hexadecimal_u16(cls, value: str | int, info: ValidationInfo) -> int:
        try:
            value_int: int = int(value, 16) if isinstance(value, str) else value
        except ValueError:
            raise ValueError(
                f"{info.field_name} must be an unsigned 16-bit integer (or hexadecimal representation of one)"
            )
        assert (
            0 <= value_int < 65536
        ), f"{info.field_name} must be an unsigned 16-bit integer (or hexadecimal representation of one)"
        return value_int


class InputDeviceBitmaps(BaseModel):
    prop: str | int
    ev: str | int
    msc: Optional[int] = None
    key: str | List[int] = []
    led: Optional[int] = None

    @field_validator("prop", "ev")
    @staticmethod
    def hex(value: str | int) -> int:
        if isinstance(value, str):
            return int(value, 16)
        else:
            return value

    @field_validator("key")
    @classmethod
    def hex_list(cls, value: str | List[int]) -> List[int]:
        int_list: List[int]
        if isinstance(value, str):
            int_list = [int(v, 16) for v in value.split()]
        else:
            int_list = value
        return int_list


class InputDevice(BaseModel):
    id: InputDeviceId
    name: str
    phys: str
    sys: str
    uniq: Optional[str] = None
    handlers: List[str] = []
    bitmaps: InputDeviceBitmaps

    @property
    def libinput_devices(self) -> List[Path]:
        ret = []
        for handler in self.handlers:
            path = Path("/dev/input").joinpath(handler)
            if settings.input.get("check_paths", True):
                if path.exists():
                    ret.append(path)
            else:
                ret.append(path)
        return ret


class InputDevices(BaseModel):
    devices: List[InputDevice] = []

    @classmethod
    def load(cls, source: Path = Path("/proc/bus/input/devices")) -> "InputDevices":
        ret = cls()

        def process(chunk: List[str]) -> InputDevice:
            logger.debug(f"Processing chunk: {chunk}")
            build: Dict[str, Any] = {}
            for start, line in map(lambda x: x.split(": ", 1), chunk):
                logger.debug(f"Processing line: {start}: {line}")
                match start:
                    case "I":
                        id_parsed = {k.lower(): v for k, v in map(lambda x: x.split("="), line.split())}
                        build["id"] = id_parsed
                        logger.debug(f"Identified device ID struct: {id_parsed}")
                    case "N":
                        name_parsed = line.split("=", 1)[-1].strip('"')
                        build["name"] = name_parsed
                        logger.debug(f"Identified device name: {name_parsed}")
                    case "P":
                        phys_parsed = line.split("=", 1)[-1]
                        build["phys"] = phys_parsed
                        logger.debug(f"Identified device physical location: {phys_parsed}")
                    case "S":
                        sys_parsed = line.split("=", 1)[-1]
                        build["sys"] = sys_parsed
                        path = Path(f"/sys{sys_parsed}")
                        if settings.input.get("check_paths", True):
                            logger.debug(f"...checking path: {path}")
                            assert path.exists(), f"Path '{path}' doesn't exist"
                        logger.debug(f"Identified device /sys path: {sys_parsed}")
                    case "U":
                        if uniq := line.split("=", 1)[-1]:
                            build["uniq"] = uniq
                            logger.debug(f"Identified device unique identifier: {uniq}")
                    case "H":
                        build["handlers"] = line.split("=", 1)[-1].split()
                        for handler in build["handlers"]:
                            if handler not in NON_DEVICE_HANDLERS:
                                path = Path("/dev/input").joinpath(handler)
                                if settings.input.get("check_paths", True):
                                    logger.debug(f"...checking path: {path}")
                                    assert path.exists(), f"Path '{path}' doesn't exist"
                            logger.debug(f"Identified input event handler device: {handler}")
                    case "B":
                        build["bitmaps"] = build.get("bitmaps", {})
                        bitmap, value = line.split("=", 1)
                        bitmap = bitmap.lower()
                        build["bitmaps"][bitmap] = value
                        logger.debug(f"Identified device bitmap {bitmap}: {value}")
                    case _:
                        raise ValueError(f"Unable to parse input prefix {start} with value {line}")
            logger.debug(f"Parsing InputDevice: {build}")
            return InputDevice(**build)

        this_chunk: List[str] = []
        with open(source) as f:
            for line in map(lambda l: l.rstrip(), f.readlines()):
                if this_chunk and not line:
                    ret.devices.append(process(this_chunk))
                    this_chunk = []
                else:
                    this_chunk.append(line)
        if this_chunk:
            ret.devices.append(process(this_chunk))
        return ret
