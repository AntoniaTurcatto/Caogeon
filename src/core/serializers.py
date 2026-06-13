from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import json

class SerializeStrategy(ABC):
    """Serialize dict to str"""
    @abstractmethod
    def serialize(self, obj) -> str:
        pass

    @abstractmethod
    def deserialize(self, data: str) -> Any:
        pass

class ObjParserStrategy(ABC):
    """Parse an object to dict"""
    @abstractmethod
    def to_dict(self, obj: Any) -> dict:
        pass

    @abstractmethod
    def from_dict(self, data: dict) -> Any:
        pass

class JSONSerializer(SerializeStrategy):
    def serialize(self, obj: Any) -> str:
        return json.dumps(obj, indent=2, ensure_ascii=False)

    def deserialize(self, data: str) -> Any:
        return json.loads(data)

class DataSerializer:
    def __init__(self, obj_parser: ObjParserStrategy, serializer: SerializeStrategy,) -> None:
        self.serializer = serializer
        self.parser = obj_parser

    def save_to_file(self, obj: Any, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.serializer.serialize(self.parser.to_dict(obj)))

    def load_from_file(self, filepath: Path) -> Any | None:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = self.parser.from_dict(self.serializer.deserialize(f.read()))
        return data
