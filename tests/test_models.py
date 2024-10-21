import pytest
from pydantic import ValidationError

from panasonic_programmable_keys.input import InputDevices
from panasonic_programmable_keys.util import settings

from .example_devices import invalid_devices
from .example_devices import valid_devices

settings.input["check_paths"] = False


@pytest.mark.parametrize("valid_device", valid_devices)
def test_valid_device_parsing(valid_device):
    """Ensure that valid /proc/bus/input/devices files can be deserialized."""
    InputDevices.load(source=valid_device)


@pytest.mark.parametrize("invalid_device", invalid_devices)
def test_invalid_device_parsing(invalid_device):
    """Ensure that invalid /proc/bus/input/devices files can be deserialized."""
    with pytest.raises(ValidationError):
        InputDevices.load(source=invalid_device)
