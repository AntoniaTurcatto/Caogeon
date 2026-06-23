from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar
import json

T = TypeVar("T")

class SerializeStrategy(ABC):
    """Serialize dict to str"""
    @abstractmethod
    def serialize(self, obj) -> str:
        pass

    @abstractmethod
    def deserialize(self, data: str) -> Any:
        pass

class ObjParserStrategy(ABC, Generic[T]):
    """Parse an object to dict"""
    @abstractmethod
    def to_dict(self, obj: T) -> dict:
        pass

    @abstractmethod
    def from_dict(self, data: dict) -> T:
        pass

class PathValidator(ABC):
    @abstractmethod
    def validate(self, path: Path) -> bool:
        pass

    @abstractmethod
    def error_msg(self, path: Path) -> str:
        pass

class JSONSerializer(SerializeStrategy):
    def serialize(self, obj: Any) -> str:
        return json.dumps(obj, indent=2, ensure_ascii=False)

    def deserialize(self, data: str) -> Any:
        return json.loads(data)

class JSONPathValidator(PathValidator):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.json'

    def error_msg(self, path: Path) -> str:
        return f"Invalid file extension: {path.suffix}. Must be .json"

class DataSerializer(Generic[T]):
    def __init__(self, obj_parser: ObjParserStrategy[T], serializer: SerializeStrategy, validator: PathValidator = JSONPathValidator()) -> None:
        self.serializer = serializer
        self.parser = obj_parser
        self.validator = validator

    def save_to_file(self, obj: T, filepath: Path):
        if not self.validator.validate(filepath):
            raise ValueError(self.validator.error_msg(filepath))

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.serializer.serialize(self.parser.to_dict(obj)))

    def load_from_file(self, filepath: Path) -> T | None:
        if not self.validator.validate(filepath):
            raise ValueError(self.validator.error_msg(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            data = self.parser.from_dict(self.serializer.deserialize(f.read()))
        return data
