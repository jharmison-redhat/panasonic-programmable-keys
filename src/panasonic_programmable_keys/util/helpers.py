from typing import Any


class Truthy(str):
    """Casting to boolean returns True when set to "true", "yes", "1", or any case of the above."""

    def __bool__(self) -> bool:
        match self.lower():
            case "true":
                return True
            case "yes":
                return True
            case "1":
                return True
            case _:
                return False


def merge(a: Any, b: Any, path: list | None = None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend([v for v in b[key] if v not in a[key]])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a
