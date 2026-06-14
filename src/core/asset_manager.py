from pathlib import Path
from .registers import Registry
from .serializers import  DataSerializer, ObjParserStrategy, SerializeStrategy
from .managers import Manager, ProjectPartsManager, ProjectPaths
from .model import Asset

class AssetParser(ObjParserStrategy[Asset]):
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
