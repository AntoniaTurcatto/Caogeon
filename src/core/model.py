from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Any

@dataclass
class ProjectPartBase:
    UNIQUE_NAME_VAR = "unique_name"
    unique_name: str

    @classmethod
    def property_types(cls) -> dict[str, type]:
        return {
          "unique_name": str,
        }

@dataclass
class PropertyChange:
    obj: ProjectPartBase
    property_name: str
    new_value: Any

@dataclass
class Asset(ProjectPartBase):
    """Class to represent a project's asset"""
    path: Path

    @classmethod
    def property_types(cls) -> dict[str, type]:
        return super().property_types() | {
            "path": Path,
        }

@dataclass
class Entity(ProjectPartBase):
    """A class to represent a type of a entity, such a certain enemy, a rock, etc"""
    sprite: Asset
    width: int
    height: int
    script_path: Path
    variables: dict[str, Any]
    hooks: dict[str, str] #[value_passed_to_on_message, real_function_within_script]

    @classmethod
    def property_types(cls) -> dict[str, type]:
        return super().property_types() | {
            "sprite": Asset,
            "width": int,
            "height": int,
            "script_path": Path,
            "variables": dict[str, Any],
            "hooks": dict[str, str],
        }

@dataclass
class InstancedEntity:
    """A wrapper around Entity that represent a instanced Entity within a scene"""
    entity: Entity
    id: str
    x: int
    y: int

    @classmethod
    def property_types(cls) -> dict[str, type]:
        return {
            "entity": Entity,
            "id": str,
            "x": int,
            "y": int,
        }

    @property
    def unique_name(self) -> str:
        return self.id

@dataclass
class Scene(ProjectPartBase):
    background: Asset | None
    entities: list[InstancedEntity]
    script_path: Path

    @classmethod
    def property_types(cls) -> dict[str, type]:
        return super().property_types() | {
            "background": Asset | None,
            "entities": list[InstancedEntity],
            "script_path": Path,
        }

    def create_instanced_entity(self, entity: Entity, x: int = 0, y: int = 0) -> InstancedEntity:
        return InstancedEntity(entity=entity, id=self.find_valid_id(entity.unique_name), x=x, y=y)

    def find_valid_id(self, id: str) -> str:
        count = 0
        while id in map(lambda e: e.id, self.entities):
            count += 1
            id = f"{id}_{count}"
        return id

@dataclass
class WindowSpecs:
    title: str
    height: int
    width: int
    target_fps: int


@dataclass
class Project:
    name: str
    engine_version: str
    window_specs: WindowSpecs
    initial_scene: Scene
