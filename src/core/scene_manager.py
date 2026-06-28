from pathlib import Path
from sys import prefix

from core.model import Asset, Entity, Scene
from core.model_parsers import InstancedEntityParser, SceneParser
from core.registers import Registry
from core.serializers import DataSerializer, SerializeStrategy
from utils.files import PathUtils
from .managers import CanCreateBlank, ProjectPartsManager, ProjectPaths, ProjectPathsState

class SceneManager(ProjectPartsManager, CanCreateBlank):
    def __init__(self,
        project_paths_state: ProjectPathsState,
        serializer_strategy: SerializeStrategy,
        assets: Registry[Asset],
        entities: Registry[Entity]) -> None:
        super().__init__(project_paths_state, DataSerializer(SceneParser(assets, InstancedEntityParser(entities)), serializer_strategy))
        self.scenes = Registry[Scene]()

    def load(self, project_paths: ProjectPaths):
        aux_scenes = Registry[Scene]()
        for filepath in project_paths.scenes_dir.glob("*.json"):
            scene = self.serializer.load_from_file(filepath)
            if scene is not None:
                aux_scenes.register(scene.unique_name, scene)
        self.scenes.replace_all(aux_scenes)

    def save(self, project_paths: ProjectPaths) -> None:
        project_paths.scenes_dir.mkdir(parents=True, exist_ok=True)
        for scene in self.scenes.all():
            filepath = project_paths.scenes_dir / f"{scene.unique_name}.json"
            self.serializer.save_to_file(scene, filepath)

    def create_blank(self) -> Scene:
        if self.project_paths_state.project_paths is None:
            return Scene(unique_name="empty scene", background=None, entities=[], script_path=Path())
        path = self.project_paths_state.project_paths.scenes_script_dir
        unique_name = self.scenes.first_valid_name("empty scene")
        scene = Scene(unique_name=unique_name, background=None, entities=[], script_path=PathUtils.create_empty_script(path, unique_name))
        self.scenes.register(unique_name, scene)
        return scene

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.scenes_dir, project_paths.scenes_script_dir]

    def registry(self) -> Registry[Scene]:
        return self.scenes
