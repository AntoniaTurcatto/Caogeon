from pathlib import Path
import shutil
from .serializers import DataSerializer

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
    def __init__(self, project_paths: ProjectPaths, serializer: DataSerializer) -> None:
        self.project_paths = project_paths
        self.serializer = serializer

    def clear_folders(self, folders: list[Path]):
        for folder in folders:
            if folder.exists():
                shutil.rmtree(folder)

    def create_folder(self, folder:Path):
        folder.mkdir(parents=True, exist_ok=True)
