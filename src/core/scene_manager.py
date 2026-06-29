from pathlib import Path
from sys import prefix

from core.model import Asset, Entity, InstancedEntity, Scene
from core.model_parsers import InstancedEntityParser, SceneParser
from core.registers import Registry
from core.serializers import DataSerializer, SerializeStrategy
from utils.files import PathUtils
from .managers import ProjectPartsManager, ProjectPaths, ProjectPathsState

class SceneManager(ProjectPartsManager):
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
        super().save(project_paths)
        project_paths.scenes_dir.mkdir(parents=True, exist_ok=True)
        for scene in self.scenes.all():
            filepath = project_paths.scenes_dir / f"{scene.unique_name}.json"
            self.serializer.save_to_file(scene, filepath)

    def create(self) -> Scene:
        """Creates a new empty scene, adds it to the registry, and returns it."""
        if self.project_paths_state.project_paths is None:
            return Scene(unique_name="empty scene", background=None, entities=[], script_path=Path())
        path = self.project_paths_state.project_paths.scenes_script_dir
        unique_name = self.scenes.first_valid_name("empty scene")
        scene = Scene(unique_name=unique_name, background=None, entities=[], script_path=PathUtils.create_empty_script(path, unique_name))
        self.scenes.register(unique_name, scene)
        return scene

    def create_instanced_entity(self, scene: Scene, entity: Entity, x: int = 0, y: int = 0) -> InstancedEntity:
        instanced_entity = scene.create_instanced_entity(entity, x, y)
        return instanced_entity

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.scenes_dir, project_paths.scenes_script_dir]

    def _folder_with_registered_type_files(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.scenes_dir]

    def registry(self) -> Registry[Scene]:
        return self.scenes

    def get_obj_filepaths(self, obj: Scene) -> list[Path]:
        return [obj.script_path]
