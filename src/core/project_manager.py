from pathlib import Path
from queue import Empty

from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.managers import Manager, ProjectPaths, ProjectPathsState
from core.model import Project, WindowSpecs
from core.model_parsers import ProjectParser, WindowSpecsParser
from core.scene_manager import SceneManager
from core.serializers import DataSerializer, JSONSerializer
from utils.files import PathUtils

class ProjectManager(Manager):
    def __init__(self) -> None:
        paths_state = ProjectPathsState()
        self.serializer_strat = JSONSerializer()
        self.asset_manager = AssetManager(paths_state, self.serializer_strat)
        self.entity_manager = EntityManager(paths_state, self.serializer_strat, self.asset_manager.assets)
        self.scene_manager = SceneManager(paths_state, self.serializer_strat, self.asset_manager.assets, self.entity_manager.entities)
        self.project = None
        super().__init__(paths_state, DataSerializer(ProjectParser(WindowSpecsParser(), self.scene_manager.scenes), self.serializer_strat))

    def load(self, project_paths: ProjectPaths):
        self.project_paths_state.project_paths = project_paths
        self.asset_manager.load(project_paths)
        self.entity_manager.load(project_paths)
        self.scene_manager.load(project_paths)
        self.project = self.serializer.load_from_file(project_paths.project_file)

    def save(self, project_paths: ProjectPaths | None = None) -> None:
        if project_paths is not None:
            if self.project_paths_state.project_paths is not None:
                self.clone_project(self.project_paths_state.project_paths, project_paths)
            self.project_paths_state.project_paths = project_paths
        if self.project_paths_state.project_paths is None:
            return

        super().save(project_paths)
        self.asset_manager.save(self.project_paths_state.project_paths)
        self.entity_manager.save(self.project_paths_state.project_paths)
        self.scene_manager.save(self.project_paths_state.project_paths)
        self.serializer.save_to_file(self.project, self.project_paths_state.project_paths.project_file)

    def import_asset(self, filepath: Path):
        if not self.project_loaded():
            raise ValueError("No project loaded")
        self.asset_manager.import_asset(filepath)

    def project_loaded(self):
        return self.project_paths_state.project_paths is not None

    def new(self, project_paths: ProjectPaths, name: str):
        super().new(project_paths)
        self.project_paths_state.project_paths = project_paths
        self.asset_manager.new(project_paths)
        self.entity_manager.new(project_paths)
        self.scene_manager.new(project_paths)
        project_paths.project_file.touch()
        self._create_empty_project(name)
        self.save()

    def clone_project(self, origin: ProjectPaths, new_path: ProjectPaths):
        """Clones project to new_path, overriding if the new_path.root folder exists"""
        PathUtils.copy_folder(origin.root, new_path.root)

    def _create_empty_project(self, name: str):
        if self.project_paths_state.project_paths is None:
            raise ValueError("Project paths not set")
        empty_scene = self.scene_manager.create()
        self.project = Project(name=name,
          engine_version="0.1", window_specs=WindowSpecs(title=name, height=600, width=800, target_fps=30), initial_scene=empty_scene)

    def _folders(self, project_paths: ProjectPaths) -> list[Path]:
        return [project_paths.root]

    def _folder_with_registered_type_files(self, project_paths: ProjectPaths) -> list[Path]:
        return []
