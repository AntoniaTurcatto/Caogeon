from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Any, Callable, Generic, TypeVar

from core.model import ProjectPartBase, PropertyChange
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

class CanCreateBlank(ABC, Generic[TProjectPartBase]):
    @abstractmethod
    def create_blank(self, project_paths: ProjectPaths) -> TProjectPartBase:
        pass

class ProjectPartsManager(Manager, Generic[TProjectPartBase]):
    def __init__(self, serializer: DataSerializer) -> None:
        super().__init__(serializer)
        # List of listeners for when an ID is updated, called with the updated object and old unique name
        self.on_id_updated: list[Callable[[ProjectPartBase, str], None]] = []

    def add_listener_id_updated(self, listener: Callable[[ProjectPartBase, str], None]):
        self.on_id_updated.append(listener)

    def update_property(self, change: PropertyChange):
        old_obj = change.obj
        old_id = old_obj.unique_name
        self._update_property(change)
        if change.obj.unique_name != old_id:
            print(f"ID updated: {old_id} -> {change.obj.unique_name}")
            for listener in self.on_id_updated:
                listener(change.obj, old_id)

    def _update_property(self, change: PropertyChange):
        property_types = change.obj.property_types()
        if change.property_name not in property_types:
            raise ValueError(f"Property '{change.property_name}' is not a valid property for {change.obj.__class__.__name__}")
        expected_type = property_types[change.property_name]
        if not isinstance(change.new_value, expected_type):
            raise ValueError(f"Property '{change.property_name}' must be of type {expected_type.__name__}")

        setattr(change.obj, change.property_name, expected_type(change.new_value))

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
