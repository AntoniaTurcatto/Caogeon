# tests/core/test_project_manager.py
import json
import pytest
from pathlib import Path
from core.project_manager import ProjectManager, WindowSpecsParser, ProjectParser
from core.model import Asset, Entity, InstancedEntity, Scene, WindowSpecs, Project
from core.registers import Registry
from core.managers import ProjectPaths

@pytest.fixture
def project_paths(tmp_path):
    return ProjectPaths(tmp_path)

@pytest.fixture
def manager():
    return ProjectManager()

def setup_project(paths: ProjectPaths):
    paths.assets_dir.mkdir(parents=True, exist_ok=True)
    paths.entities_dir.mkdir(parents=True, exist_ok=True)
    paths.scenes_dir.mkdir(parents=True, exist_ok=True)

    (paths.assets_dir / "sprite.json").write_text(json.dumps(
        {"unique_name": "sprite", "path": "assets/sprite.png"}
    ))
    (paths.entities_dir / "meu_buneco.json").write_text(json.dumps({
        "unique_name": "meu_buneco", "sprite_name": "sprite",
        "width": 5, "height": 10, "script_path": str(paths.entities_script_dir / "buneco.py"),
        "variables": {"vida": 100}, "hooks": {"on_spawn": "inicializar"},
    }))
    (paths.scenes_dir / "level01.json").write_text(json.dumps({
        "unique_name": "level01", "background": "sprite",
        "entities": [{"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}],
        "script_path": str(paths.scenes_script_dir / "level01.py")
    }))
    paths.project_file.write_text(json.dumps({
        "name": "Caogeon Demo", "engine_version": "1.0.0",
        "window": {"title": "Janela", "width": 800, "height": 600, "target_fps": 60},
        "initial_scene_name": "level01",
    }))

# --- WindowSpecsParser ---

def test_window_roundtrip():
    parser = WindowSpecsParser()
    original = WindowSpecs(title="Janela", width=800, height=600, target_fps=60)
    assert parser.from_dict(parser.to_dict(original)) == original

# --- ProjectParser ---

def test_project_parser_resolves_initial_scene(project_paths):
    scenes = Registry()
    scene = Scene(unique_name="level01", background=Asset("bg", Path("bg.png")), entities=[], script_path=project_paths.scenes_script_dir / "level01.py")
    scenes.register("level01", scene)
    parser = ProjectParser(WindowSpecsParser(), scenes)
    data = {
        "name": "Demo", "engine_version": "1.0.0",
        "window": {"title": "J", "width": 800, "height": 600, "target_fps": 60},
        "initial_scene_name": "level01",
    }
    project = parser.from_dict(data)
    assert project.initial_scene is scene

def test_project_parser_unknown_scene_raises():
    parser = ProjectParser(WindowSpecsParser(), Registry())
    data = {
        "name": "Demo", "engine_version": "1.0.0",
        "window": {"title": "J", "width": 800, "height": 600, "target_fps": 60},
        "initial_scene_name": "nao_existe",
    }
    with pytest.raises(KeyError):
        parser.from_dict(data)

# --- ProjectManager.load ---

def test_project_is_none_before_load(manager):
    assert manager.project is None

def test_load_populates_project(manager, project_paths):
    setup_project(project_paths)
    manager.load(project_paths)
    assert manager.project is not None
    assert manager.project.name == "Caogeon Demo"

def test_load_populates_all_registries(manager, project_paths):
    setup_project(project_paths)
    manager.load(project_paths)
    assert manager.asset_manager.assets.get("sprite") is not None
    assert manager.entity_manager.entities.get("meu_buneco") is not None
    assert manager.scene_manager.scenes.get("level01") is not None

def test_load_cross_references(manager, project_paths):
    setup_project(project_paths)
    manager.load(project_paths)
    entity = manager.entity_manager.entities.get("meu_buneco")
    assert entity.sprite.unique_name == "sprite"
    scene = manager.scene_manager.scenes.get("level01")
    assert scene.entities[0].entity is entity

# --- ProjectManager.save ---

def test_save_creates_all_files(manager, project_paths):
    setup_project(project_paths)
    manager.load(project_paths)
    manager.save(project_paths)
    assert (project_paths.assets_dir / "sprite.json").exists()
    assert (project_paths.entities_dir / "meu_buneco.json").exists()
    assert (project_paths.scenes_dir / "level01.json").exists()
    assert project_paths.project_file.exists()

def test_save_load_roundtrip(manager, project_paths):
    setup_project(project_paths)
    manager.load(project_paths)
    original = manager.project
    manager.save(project_paths)

    manager2 = ProjectManager()
    manager2.load(project_paths)
    assert manager2.project == original
