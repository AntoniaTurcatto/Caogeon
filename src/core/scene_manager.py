from core.model import Asset, Entity, InstancedEntity, Scene
from core.registers import Registry
from core.serializers import DataSerializer, ObjParserStrategy, SerializeStrategy
from .managers import Manager, ProjectPaths

class InstancedEntityParser(ObjParserStrategy):
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

class SceneParser(ObjParserStrategy):
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
                 project_paths: ProjectPaths, 
                 serializer_strategy: SerializeStrategy, 
                 assets: Registry[Asset], 
                 entities: Registry[Entity]) -> None:
        super().__init__(project_paths, DataSerializer(SceneParser(assets, InstancedEntityParser(entities)), serializer_strategy))
        self.scenes = Registry[Scene]()
