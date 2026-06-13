from pathlib import Path
from core.model import Asset, Entity
from core.registers import Registry
from .managers import ProjectPaths, Manager
from .serializers import DataSerializer, ObjParserStrategy, SerializeStrategy

class EntityManager(Manager):
    def __init__(self, project_paths: ProjectPaths, serializer_strategy: SerializeStrategy, assets: Registry[Asset]) -> None:
        super().__init__(project_paths, DataSerializer(EntityParser(assets), serializer_strategy))
        self.entities = Registry[Entity]()

class EntityParser(ObjParserStrategy):
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
