from pathlib import Path
from queue import Empty

from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.managers import Manager, ProjectPaths
from core.model import Project, Scene, WindowSpecs
from core.model_parsers import ProjectParser, WindowSpecsParser
from core.scene_manager import SceneManager
from core.serializers import DataSerializer, JSONSerializer

class ProjectManager(Manager):
    def __init__(self) -> None:
        self.serializer_strat = JSONSerializer()
        self.proj_paths: ProjectPaths | None = None
        self.asset_manager = AssetManager(self.proj_paths, self.serializer_strat)
        self.entity_manager = EntityManager(self.proj_paths, self.serializer_strat, self.asset_manager.assets)
        self.scene_manager = SceneManager(self.proj_paths, self.serializer_strat, self.asset_manager.assets, self.entity_manager.entities)

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

    def import_asset(self, filepath: Path):
        if not self.project_loaded():
            raise ValueError("No project loaded")
        self.asset_manager.import_asset(filepath)

    def project_loaded(self):
        return self.proj_paths is not None

    def new(self, project_paths: ProjectPaths, name: str):
        super().new(project_paths)
        self.proj_paths = project_paths
        self.asset_manager.new(project_paths)
        self.entity_manager.new(project_paths)
        self.scene_manager.new(project_paths)
        project_paths.project_file.touch()
        self._create_empty_project(name)
        self.save()

    def _create_empty_project(self, name: str):
        if self.proj_paths is None:
            raise ValueError("Project paths not set")
        empty_scene = self.scene_manager.create_blank(self.proj_paths)
        self.project = Project(name=name,
          engine_version="0.1", window_specs=WindowSpecs(title=name, height=600, width=800, target_fps=30), initial_scene=empty_scene)

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.root]
