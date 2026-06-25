from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any, Callable, Generic, TypeVar

from core.model import ProjectPartBase
from core.registers import Registry

from .serializers import DataSerializer

TProjectPartBase = TypeVar("TProjectPartBase", bound=ProjectPartBase)

class ProjectPaths:
    def __init__(self, project_path: str | Path):
        self.root = Path(project_path)
        self.assets_dir = Path(self.root / "assets")
        self.assets_files_dir = Path(self.root / "assets_files")
        self.entities_dir = Path(self.root / "entities")
        self.scenes_dir = Path(self.root / "scenes")
        self.scenes_script_dir = Path(self.root / "scenes" / "scripts")
        self.entities_script_dir = Path(self.root / "scripts")
        self.project_file = Path(self.root / "project.json")

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
        self.clear_folders(self._folders(project_paths))
        for folder in self._folders(project_paths):
            self.create_folder(folder)

    @abstractmethod
    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        pass

    @abstractmethod
    def load(self, project_paths: ProjectPaths):
        pass

    @abstractmethod
    def save(self, project_paths: ProjectPaths | None = None):
        pass

class ProjectPartsManager(Manager, Generic[TProjectPartBase]):
    def __init__(self, serializer: DataSerializer) -> None:
        super().__init__(serializer)
        # List of listeners for when an ID is updated, called with the updated object and old unique name
        self.on_id_updated: list[Callable[[TProjectPartBase, str], None]] = []

    def add_listener_id_updated(self, listener: Callable[[TProjectPartBase, str], None]):
        self.on_id_updated.append(listener)

    def update_property(self, unique_name: str, property_name: str, new_value: str):
        obj = self.get(unique_name)
        if obj is None:
            return
        old_id = obj.unique_name
        self._update_property(obj, property_name, new_value)
        if property_name == obj.UNIQUE_NAME_VAR:
            print(f"ID updated: {old_id} -> {new_value}")
            for listener in self.on_id_updated:
                listener(obj, old_id)

    def _update_property(self, obj: TProjectPartBase, property_name: str, new_value: str):
        property_types = obj.property_types()
        if property_name not in property_types:
            raise ValueError(f"Property '{property_name}' is not a valid property for {obj.__class__.__name__}")
        expected_type = property_types[property_name]
        if not isinstance(new_value, expected_type):
            raise ValueError(f"Property '{property_name}' must be of type {expected_type.__name__}")

        setattr(obj, property_name, expected_type(new_value))

    def get_as_dict(self, unique_name: str) -> dict:
        obj = self.get(unique_name)
        if obj is None:
            return {}
        return self.serializer.parser.to_dict(obj)

    def add(self, obj: TProjectPartBase):
        obj.unique_name = self.registry().first_valid_name(obj.unique_name)
        self.registry().register(obj.unique_name, obj)

    def get(self, unique_name: str) -> TProjectPartBase | None:
        return self.registry().try_get(unique_name)

    def remove(self, unique_name: str):
        self.registry().unregister(unique_name)

    @abstractmethod
    def registry(self) -> Registry[TProjectPartBase]:
        pass
