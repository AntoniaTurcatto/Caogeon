from pathlib import Path

from core.model import Asset, Entity
from core.model_parsers import EntityParser
from core.registers import Registry
from utils.files import PathUtils
from .managers import ProjectPartsManager, ProjectPaths, ProjectPathsState
from .serializers import DataSerializer, SerializeStrategy

class EntityManager(ProjectPartsManager):
    def __init__(self, project_paths_state: ProjectPathsState, serializer_strategy: SerializeStrategy, assets: Registry[Asset]) -> None:
        super().__init__(project_paths_state, DataSerializer(EntityParser(assets), serializer_strategy))
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

    def create(self, asset: Asset) -> Entity | None:
        """Creates a new entity from the given asset, adds it to the registry, and returns it."""
        if self.project_paths_state.project_paths is None:
          return None
        unique_name = self.registry().first_valid_name("blank entity")
        entity = Entity(
            unique_name=unique_name,
            sprite=asset,
            width=50,
            height=50,
            script_path=PathUtils.create_empty_script(self.project_paths_state.project_paths.entities_script_dir, unique_name),
            variables={},
            hooks={}
        )
        self.registry().register(entity.unique_name, entity)
        return entity

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.entities_dir, project_paths.entities_script_dir]

    def registry(self) -> Registry[Entity]:
        return self.entities
