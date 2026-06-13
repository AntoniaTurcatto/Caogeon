from pathlib import Path
from core.registers import Registry
from .serializers import  DataSerializer, ObjParserStrategy, SerializeStrategy
from .managers import Manager, ProjectPaths
from .model import Asset

class AssetManager(Manager):
    def __init__(self, projectPaths: ProjectPaths, serializer_strategy: SerializeStrategy) -> None:
        super().__init__(projectPaths, DataSerializer(AssetParser(), serializer_strategy))
        self.assets = Registry[Asset]()

    def clean_assets(self):
        self.clear_folders([self.project_paths.assets_dir])
        self.create_folder(self.project_paths.assets_dir)
        self.create_folder(self.project_paths.assets_files_dir)

class AssetParser(ObjParserStrategy):
    def to_dict(self, asset: Asset) -> dict:
        data = {
            "unique_name": asset.unique_name,
            "path": str(asset.path),
        }
        return data

    def from_dict(self, data: dict) -> Asset:
        return Asset(
            unique_name=data["unique_name"],
            path=Path(data["path"])
        )
