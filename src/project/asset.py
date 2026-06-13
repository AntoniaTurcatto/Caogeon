from pathlib import Path
from .io import DataSerializer, Manager, ProjectPaths
from dataclasses import dataclass, field
import json

class AssetManager(Manager):
    def __init__(self, projectPaths: ProjectPaths) -> None:
        super().__init__(projectPaths, AssetSerializer())

    def clean_assets(self):
        self.clear_folders([self.project_paths.assets_dir])
        self.create_folder(self.project_paths.assets_dir)
        self.create_folder(self.project_paths.assets_files_dir)

@dataclass
class Asset:
    """Class to represent an Asset"""
    unique_name: str
    path: Path

class AssetSerializer(DataSerializer):
    def to_dict(self, asset: Asset) -> dict:
        data = {
            "unique_name": asset.unique_name,
            "path": str(asset.path),
        }
        return data

    def from_dict(self, data: dict) -> Asset:
        return Asset(
            unique_name=data["unique_name"],
            path=Path(data.get("path", "")),
        )

    def save_to_file(self, asset: Asset):
        asset.path.parent.mkdir(parents=True, exist_ok=True)
        with open(asset.path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(asset), f, indent=2, ensure_ascii=False)

    def load_from_file(self, filepath: Path) -> Asset | None:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self.from_dict(data)
