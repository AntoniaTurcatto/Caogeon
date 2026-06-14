from pathlib import Path
from core.model import Asset, Entity
from core.registers import Registry
from .managers import ProjectPaths, Manager
from .serializers import DataSerializer, ObjParserStrategy, SerializeStrategy

class EntityParser(ObjParserStrategy[Entity]):
    def __init__(self, assets: Registry[Asset]) -> None:
        self.assets = assets

    def to_dict(self, entity: Entity) -> dict:
        return {
            "unique_name": entity.unique_name,
            "sprite_name": entity.sprite.unique_name,
            "width": entity.width,
            "height": entity.height,
            "script_path": str(entity.script_path),
            "variables": entity.variables,
            "hooks": entity.hooks,
        }

    def from_dict(self, data: dict) -> Entity:
        return Entity(
            unique_name=data["unique_name"],
            sprite=self.assets.get(data["sprite_name"]),  # resolve referência
            width=data["width"],
            height=data["height"],
            script_path=Path(data["script_path"]),
            variables=data.get("variables", {}),
            hooks=data.get("hooks", {}),
        )

class EntityManager(Manager):
    def __init__(self, serializer_strategy: SerializeStrategy, assets: Registry[Asset]) -> None:
        super().__init__(DataSerializer(EntityParser(assets), serializer_strategy))
        self.entities = Registry[Entity]()
    
    def load(self, project_paths: ProjectPaths):
        aux_entities = Registry[Entity]()
        for filepath in project_paths.entities_dir.glob("*.json"):
            entity = self.serializer.load_from_file(filepath)
            if entity is not None:
                aux_entities.register(entity.unique_name, entity)
        self.entities.replace_all(aux_entities)

    def save(self, project_paths: ProjectPaths):
        project_paths.entities_dir.mkdir(parents=True, exist_ok=True)
        for entity in self.entities.all():
            filepath = project_paths.entities_dir / f"{entity.unique_name}.json"
            self.serializer.save_to_file(entity, filepath)
