from pathlib import Path

examples_dir = Path(__file__).parent.joinpath("examples")

valid_devices = [examples_dir.joinpath("fz40-devices"), examples_dir.joinpath("non-panasonic-devices")]
invalid_devices = [examples_dir.joinpath("malformed-devices")]