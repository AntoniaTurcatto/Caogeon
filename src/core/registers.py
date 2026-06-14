from typing import Generic, TypeVar

T = TypeVar('T')

class Registry(Generic[T]):
    def __init__(self) -> None:
        self._data: dict[str, T] = {}

    def register(self, key: str, obj: T) -> None:
        self._data[key] = obj

    def get(self, key: str) -> T:
        if key not in self._data:
            raise KeyError(f"'{key}' not found in registry")
        return self._data[key]

    def all(self) -> list[T]:
        return list(self._data.values())

    def clear(self):
        self_data = {}

    def replace_all(self, other: "Registry[T]"):
        self._data.clear()
        self._data.update(other._data)
