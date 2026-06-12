from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import shutil

class DataSerializer(ABC):
    @abstractmethod
    def load_from_file(self, obj) -> Any:
        pass
    
    @abstractmethod
    def save_to_file(self, obj):
        pass

class ProjectPaths:
    def __init__(self, project_path: str | Path):
        self.root = Path(project_path)
        self.assets_dir = Path(self.root / "model" / "assets")
        self.assets_files_dir = Path(self.root / "model" / "assets_files")
        self.entities_dir = Path(self.root / "model" / "entities")
        self.scenes_dir = Path(self.root / "model" / "scenes")
        self.script_dir = Path(self.root / "model" / "scripts")
        self.project_file = Path(self.root / "model" / "project.json")

class Manager:
    def __init__(self, project_paths: ProjectPaths) -> None:
        self.project_paths = project_paths

    def clear_folders(self, folders: list[Path]):
        for folder in folders:
            if folder.exists():
                shutil.rmtree(folder)

    def create_folder(self, folder:Path):
        folder.mkdir(parents=True, exist_ok=True)
