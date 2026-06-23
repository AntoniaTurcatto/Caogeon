from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.managers import Manager, ProjectPaths
from core.model_parsers import ProjectParser, WindowSpecsParser
from core.scene_manager import SceneManager
from core.serializers import DataSerializer, JSONSerializer

class ProjectManager(Manager):
    def __init__(self) -> None:
        self.serializer_strat = JSONSerializer()
        self.asset_manager = AssetManager(self.serializer_strat)
        self.entity_manager = EntityManager(self.serializer_strat, self.asset_manager.assets)
        self.scene_manager = SceneManager(self.serializer_strat, self.asset_manager.assets, self.entity_manager.entities)
        self.proj_paths: ProjectPaths | None = None
        self.project = None
        super().__init__(DataSerializer(ProjectParser(WindowSpecsParser(), self.scene_manager.scenes), self.serializer_strat))

    def load(self, project_paths: ProjectPaths):
        self.proj_paths = project_paths
        self.asset_manager.load(project_paths)
        self.entity_manager.load(project_paths)
        self.scene_manager.load(project_paths)
        self.project = self.serializer.load_from_file(project_paths.project_file)

    def save(self, project_paths: ProjectPaths | None = None) -> None:
        if project_paths is not None:
            self.proj_paths = project_paths
        if self.proj_paths is None:
            return
        self.asset_manager.save(self.proj_paths)
        self.entity_manager.save(self.proj_paths)
        self.scene_manager.save(self.proj_paths)
        self.serializer.save_to_file(self.project, self.proj_paths.project_file)
