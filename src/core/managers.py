from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any

from .serializers import DataSerializer

class ProjectPaths:
    def __init__(self, project_path: str | Path):
        self.root = Path(project_path)
        self.assets_dir = Path(self.root / "model" / "assets")
        self.assets_files_dir = Path(self.root / "model" / "assets_files")
        self.entities_dir = Path(self.root / "model" / "entities")
        self.scenes_dir = Path(self.root / "model" / "scenes")
        self.scenes_script_dir = Path(self.root / "model" / "scenes" / "scripts")
        self.entities_script_dir = Path(self.root / "model" / "scripts")
        self.project_file = Path(self.root / "model" / "project.json")

class Manager(ABC):
    def __init__(self, serializer: DataSerializer) -> None:
        self.serializer = serializer

    def clear_folders(self, folders: list[Path]):
        for folder in folders:
            if folder.exists():
                shutil.rmtree(folder)

    def create_folder(self, folder:Path):
        folder.mkdir(parents=True, exist_ok=True)

    def new(self, project_paths: ProjectPaths):
      pass

    @abstractmethod
    def load(self, project_paths: ProjectPaths):
        pass

    @abstractmethod
    def save(self, project_paths: ProjectPaths | None = None):
        pass

class ProjectPartsManager(Manager):
    @abstractmethod
    def add(self, obj: Any):
        pass

    @abstractmethod
    def remove(self, unique_name: str):
        pass

    @abstractmethod
    def get_as_dict(self, unique_name: str) -> dict:
        pass

    @abstractmethod
    def update_property(self, unique_name: str, property_name: str, new_value: str):
        pass

    @abstractmethod
    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        pass

    def new(self, project_paths: ProjectPaths):
        self.clear_folders(self._folders(project_paths))
        for folder in self._folders(project_paths):
            self.create_folder(folder)
