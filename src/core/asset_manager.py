from pathlib import Path

from core.model_parsers import AssetParser
from utils.files import PathUtils
from .registers import Registry
from .serializers import DataSerializer, SerializeStrategy
from .managers import ProjectPartsManager, ProjectPaths, ProjectPathsState
from .model import Asset

class AssetManager(ProjectPartsManager):
    def __init__(self, project_paths_state: ProjectPathsState, serializer_strategy: SerializeStrategy) -> None:
        super().__init__(project_paths_state, DataSerializer(AssetParser(), serializer_strategy))
        self.assets = Registry[Asset]()

    def load(self, project_paths: ProjectPaths):
        aux_assets = Registry[Asset]()
        for filepath in project_paths.assets_dir.glob("*.json"):
            asset = self.serializer.load_from_file(filepath)
            if asset is not None:
                aux_assets.register(asset.unique_name, asset)
        self.assets.replace_all(aux_assets)

    def save(self, project_paths: ProjectPaths):
        super().save(project_paths)
        project_paths.assets_dir.mkdir(parents=True, exist_ok=True)
        for asset in self.assets.all():
            filepath = project_paths.assets_dir / f"{asset.unique_name}.json"
            self.serializer.save_to_file(asset, filepath)

    def registry(self) -> Registry[Asset]:
        return self.assets

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.assets_dir, project_paths.assets_files_dir]

    def _folder_with_registered_type_files(self, project_paths: ProjectPaths) -> list[Path]:
      return [project_paths.assets_dir]

    def import_asset(self, filepath: Path):
        proj_paths = self.project_paths_state.project_paths
        if proj_paths is None:
          return
        new_file_path = proj_paths.assets_files_dir / filepath.name
        new_file_path = PathUtils.copy_file(filepath, new_file_path)
        asset = Asset(unique_name=new_file_path.stem, path=new_file_path)
        self.add(asset)

    def get_obj_filepaths(self, obj: Asset) -> list[Path]:
        return [obj.path]
