from typing import Any, Optional


class DotDict(dict):
    def __setattr__(self, name: str, value: Any) -> None:
        return super().__setitem__(name, value)

    def __getattr__(self, name: str) -> Any:
        try:
            return super().__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __delattr__(self, name: str) -> None:
        return super().__delitem__(name)

    def __init__(self, dict: Optional[dict] = None):
        if dict is not None:
            for key, value in dict.items():
                if hasattr(value, "keys"):
                    value = DotDict(value)
                self[key] = value
