from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

class ProjectPart(Enum):
    ASSETS = "assets"
    ENTITIES = "entities"
    SCENES = "scenes"

@dataclass
class Asset:
    """Class to represent a project's asset"""
    unique_name: str
    path: Path

@dataclass
class Entity:
    """A class to represent a type of a entity, such a certain enemy, a rock, etc"""
    unique_name: str
    sprite: Asset
    width: int
    height: int
    script_path: Path
    variables: dict[str, Any]
    hooks: dict[str, str] #[value_passed_to_on_message, real_function_within_script]

@dataclass
class InstancedEntity:
    """A wrapper around Entity that represent a instanced Entity within a scene"""
    entity: Entity
    id: str
    x: int
    y: int

@dataclass
class Scene:
    unique_name: str
    background: Asset
    entities: list[InstancedEntity]
    script_path: Path

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
