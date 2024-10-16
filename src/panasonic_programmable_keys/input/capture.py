import struct
from pathlib import Path
from typing import Any
from typing import Iterator

from pydantic import ValidationError

from ..util import logger
from ..util import settings
from .models import InputDevices
from .models import KeyPressEvent


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


def yield_from(device_path: Path | None = None) -> Iterator[KeyPressEvent]:
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
                _, _, _, _, _, descriptor, event = struct.unpack("4IHHI", data)
                try:
                    yield KeyPressEvent(descriptor=descriptor, type=event)
                except ValidationError:
                    continue
    else:
        raise RuntimeError("Unable to find Panasonic keyboard device event handler")