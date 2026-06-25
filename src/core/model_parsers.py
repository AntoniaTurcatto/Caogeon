from pathlib import Path
from core.model import Asset, Entity, InstancedEntity, Project, Scene, WindowSpecs
from core.registers import Registry
from core.serializers import ObjParserStrategy

class AssetParser(ObjParserStrategy[Asset]):
    def to_dict(self, asset: Asset) -> dict:
        data = {
            "unique_name": asset.unique_name,
            "path": str(asset.path),
        }
        return data

    def from_dict(self, data: dict) -> Asset:
        return Asset(
            unique_name=data["unique_name"],
            path=Path(data["path"])
        )

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
            "background": scene.background.unique_name if scene.background else "",
            "entities": [self.instanced_entity_parser.to_dict(e) for e in scene.entities],
            "script_path": str(scene.script_path),
        }
        return data

    def from_dict(self, data: dict) -> Scene:
        background = self.assets.try_get(data["background"])
        if background is None and data["background"] != "":
            raise ValueError(f"Background asset not found: {data['background']}")

        return Scene(
            unique_name = data["unique_name"],
            background  = background,
            entities    = [self.instanced_entity_parser.from_dict(e) for e in data["entities"]],
            script_path = Path(data["script_path"]),
        )

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
