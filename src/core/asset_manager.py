from pathlib import Path

from core.model_parsers import AssetParser
from .registers import Registry
from .serializers import  DataSerializer, SerializeStrategy
from .managers import ProjectPartsManager, ProjectPaths
from .model import Asset

class AssetManager(ProjectPartsManager):
    def __init__(self,  serializer_strategy: SerializeStrategy) -> None:
        super().__init__(DataSerializer(AssetParser(), serializer_strategy))
        self.assets = Registry[Asset]()

    def load(self, project_paths: ProjectPaths):
        aux_assets = Registry[Asset]()
        for filepath in project_paths.assets_dir.glob("*.json"):
            asset = self.serializer.load_from_file(filepath)
            if asset is not None:
                aux_assets.register(asset.unique_name, asset)
        self.assets.replace_all(aux_assets)

    def save(self, project_paths: ProjectPaths):
        project_paths.assets_dir.mkdir(parents=True, exist_ok=True)
        for asset in self.assets.all():
            filepath = project_paths.assets_dir / f"{asset.unique_name}.json"
            self.serializer.save_to_file(asset, filepath)

    def add(self, obj: Asset):
        if self.assets.exists(obj.unique_name):
            raise KeyError("Asset already existent")

        self.assets.register(obj.unique_name, obj)

    def remove(self, unique_name: str):
        self.assets.unregister(unique_name)

    def get_as_dict(self, unique_name: str) -> dict:
        asset = self.assets.get(unique_name)
        if asset is None:
            return {}
        return self.serializer.parser.to_dict(asset)

    def update_property(self, unique_name: str, property_name: str, new_value: str):
        asset = self.assets.get(unique_name)
        if asset is not None and hasattr(asset, property_name):
            setattr(asset, property_name, new_value)

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.assets_dir, project_paths.assets_files_dir]
