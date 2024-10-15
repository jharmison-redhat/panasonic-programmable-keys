import struct
from pathlib import Path
from typing import Any
from typing import Iterator

from ..util import logger
from ..util import settings
from .models import InputDevices


def panasonic_keyboard_device_path(devices: InputDevices | None = None) -> Path | None:
    if devices is None:
        devices = InputDevices.load()
    for device in devices.devices:
        if device.phys == "panasonic/hkey0":
            logger.debug(f"Found Panasonic keyboard: {device.name}")
            for handler in device.handlers:
                if handler.name.startswith("event") and handler.libinput_device is not None:
                    logger.debug(f"Found libinput event handler: {handler.libinput_device}")
                    return handler.libinput_device
    return None


def yield_from(device_path: Path | None = None) -> Iterator[Any]:
    # Force check paths to prevent reads on wrong device
    settings.input["check_paths"] = True

    if device_path is None:
        device_path = panasonic_keyboard_device_path()
    if device_path is not None:
        with open(device_path, "rb") as f:
            while True:
                data = f.read(24)
                if not data:
                    break
                yield struct.unpack("4IHHI", data)
    else:
        raise RuntimeError("Unable to find Panasonic keyboard device event handler")
