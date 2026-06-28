from typing import Callable, Generic, TypeVar

T = TypeVar('T')

class Registry(Generic[T]):
    def __init__(self) -> None:
        self._data: dict[str, T] = {}
        self.on_change: list[Callable] = []
        self.on_add_remove: list[Callable] = []

    def __iter__(self):
        return iter(self._data.values())

    def register(self, key: str, obj: T) -> None:
        self._data[key] = obj
        self._dispatch_on_change()
        self._dispatch_on_add_remove()

    def unregister(self, key: str):
        self._data.pop(key)
        self._dispatch_on_change()
        self._dispatch_on_add_remove()

    def get(self, key: str) -> T:
        if key not in self._data:
            raise KeyError(f"'{key}' not found in registry")
        return self._data[key]

    def try_get(self, key: str) -> T | None:
        try:
            return self.get(key)
        except:
            return None

    def exists(self, key) -> bool:
        return self.try_get(key) is not None

    def all(self) -> list[T]:
        return list(self._data.values())

    def replace_all(self, other: "Registry[T]"):
        self._data.clear()
        self._data.update(other._data)
        self._dispatch_on_change()
        self._dispatch_on_add_remove()

    def as_list(self) -> list[T]:
        return list(self._data.values())

    def first_valid_name(self, base_name: str) -> str:
        if not self.exists(base_name):
            return base_name
        count = 1
        while True:
            new_name = f"{base_name}_{count}"
            if not self.exists(new_name):
                return new_name
            count += 1

    def _dispatch_on_change(self):
        for callback in self.on_change:
            callback()

    def _dispatch_on_add_remove(self):
        for callback in self.on_add_remove:
            callback()
