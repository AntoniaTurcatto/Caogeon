from core.model import Asset, Entity, InstancedEntity, Scene
from core.registers import Registry
from core.serializers import DataSerializer, ObjParserStrategy, SerializeStrategy
from .managers import Manager, ProjectPaths

class InstancedEntityParser(ObjParserStrategy[InstancedEntity]):
    def __init__(self, entities: Registry[Entity]) -> None:
        super().__init__()
        self.entities = entities 

    def to_dict(self, instanced: InstancedEntity) -> dict:
        return {
            "id": instanced.id,
            "entity_name": instanced.entity.unique_name,  
            "x": instanced.x,
            "y": instanced.y,
        }

    def from_dict(self, data: dict) -> InstancedEntity:
        return InstancedEntity(
            id=data["id"],
            entity=self.entities.get(data["entity_name"]),
            x=data["x"],
            y=data["y"],
        )

class SceneParser(ObjParserStrategy[Scene]):
    def __init__(self, assets: Registry[Asset], instanced_entity_parser: InstancedEntityParser) -> None:
        super().__init__()
        self.assets = assets 
        self.instanced_entity_parser = instanced_entity_parser
        
    def to_dict(self, scene: Scene) -> dict:
        data = {
            "unique_name": scene.unique_name,
            "background": scene.background.unique_name,
            "entities": [self.instanced_entity_parser.to_dict(e) for e in scene.entities]
        }
        return data

    def from_dict(self, data: dict) -> Scene:
        return Scene(
            unique_name = data["unique_name"],
            background  = self.assets.get(data["background"]),
            entities    = [self.instanced_entity_parser.from_dict(e) for e in data["entities"]]
        )



class SceneManager(Manager):
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
