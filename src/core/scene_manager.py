from core.model import Asset, Entity, Scene
from core.model_parsers import InstancedEntityParser, SceneParser
from core.registers import Registry
from core.serializers import DataSerializer, SerializeStrategy
from .managers import ProjectPartsManager, ProjectPaths

class SceneManager(ProjectPartsManager):
    def __init__(self,
                serializer_strategy: SerializeStrategy,
                 assets: Registry[Asset],
                 entities: Registry[Entity]) -> None:
        super().__init__(DataSerializer(SceneParser(assets, InstancedEntityParser(entities)), serializer_strategy))
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

    def add(self, obj: Scene):
        if self.scenes.exists(obj.unique_name):
            raise KeyError("Scene already existent")

        self.scenes.register(obj.unique_name, obj)

    def remove(self, unique_name: str):
        self.scenes.unregister(unique_name)

    def get_as_dict(self, unique_name: str) -> dict:
        scene = self.scenes.get(unique_name)
        if scene is None:
            return {}
        return self.serializer.parser.to_dict(scene)

    def update_property(self, unique_name: str, property_name: str, new_value: str):
        scene = self.scenes.get(unique_name)
        if scene is not None and hasattr(scene, property_name):
            setattr(scene, property_name, new_value)
