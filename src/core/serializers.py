from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass, field
import json
from typing import Any

class DataSerializer(ABC):
    @abstractmethod
    def load_from_file(self, filepath: Path) -> Any | None:
        pass
    
    @abstractmethod
    def save_to_file(self, obj):
        pass
