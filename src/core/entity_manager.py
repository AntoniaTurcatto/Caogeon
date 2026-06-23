from pathlib import Path

from core.model import Asset, Entity
from core.model_parsers import EntityParser
from core.registers import Registry
from .managers import ProjectPartsManager, ProjectPaths
from .serializers import DataSerializer, SerializeStrategy

class EntityManager(ProjectPartsManager):
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

    def add(self, obj: Entity):
        if self.entities.exists(obj.unique_name):
            raise KeyError("Entity already existent")

        self.entities.register(obj.unique_name, obj)

    def remove(self, unique_name: str):
        self.entities.unregister(unique_name)

    def get_as_dict(self, unique_name: str) -> dict:
        entity = self.entities.get(unique_name)
        if entity is None:
            return {}
        return self.serializer.parser.to_dict(entity)

    def update_property(self, unique_name: str, property_name: str, new_value: str):
        entity = self.entities.get(unique_name)
        if entity is not None and hasattr(entity, property_name):
            setattr(entity, property_name, new_value)

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.entities_dir, project_paths.entities_script_dir]
