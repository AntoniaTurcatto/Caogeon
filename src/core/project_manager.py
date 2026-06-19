from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.managers import Manager, ProjectPaths
from core.model import Project, Scene, WindowSpecs
from core.registers import Registry
from core.scene_manager import SceneManager
from core.serializers import DataSerializer, JSONSerializer, ObjParserStrategy

class WindowSpecsParser(ObjParserStrategy[WindowSpecs]):
    def to_dict(self, window: WindowSpecs) -> dict:
        data = {
            "title": window.title,
            "width": window.width,
            "height": window.height,
            "target_fps": window.target_fps
        }
        return data

    def from_dict(self, data: dict) -> WindowSpecs:
        return WindowSpecs(
            title=data["title"],
            width=data["width"],
            height=data["height"],
            target_fps=data["target_fps"]
        )

class ProjectParser(ObjParserStrategy[Project]):
    def __init__(self, window_parser: WindowSpecsParser, scenes: Registry[Scene]) -> None:
        super().__init__()
        self.window_parser = window_parser
        self.scenes = scenes


    def to_dict(self, project: Project) -> dict:
        data = {
            "name": project.name,
            "engine_version": project.engine_version,
            "window": self.window_parser.to_dict(project.window_specs),
            "initial_scene_name": project.initial_scene.unique_name
        }
        return data

    def from_dict(self, data: dict) -> Project:
        return Project(
            name=data["name"],
            engine_version=data["engine_version"],
            window_specs=self.window_parser.from_dict(data["window"]),
            initial_scene=self.scenes.get(data["initial_scene_name"])
        )

class ProjectManager(Manager):
    def __init__(self) -> None:
        self.serializer_strat = JSONSerializer()
        self.asset_manager = AssetManager(self.serializer_strat)
        self.entity_manager = EntityManager(self.serializer_strat, self.asset_manager.assets)
        self.scene_manager = SceneManager(self.serializer_strat, self.asset_manager.assets, self.entity_manager.entities)
        self.project = None
        super().__init__(DataSerializer(ProjectParser(WindowSpecsParser(), self.scene_manager.scenes), self.serializer_strat))

    def load(self, project_paths: ProjectPaths):
        self.asset_manager.load(project_paths)
        self.entity_manager.load(project_paths)
        self.scene_manager.load(project_paths)
        self.project = self.serializer.load_from_file(project_paths.project_file)

    def save(self, project_paths: ProjectPaths) -> None:
        self.asset_manager.save(project_paths)
        self.entity_manager.save(project_paths)
        self.scene_manager.save(project_paths)
        self.serializer.save_to_file(self.project, project_paths.project_file)
