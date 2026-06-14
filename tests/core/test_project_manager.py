import json
import pytest
from core.project_manager import ProjectManager, WindowSpecsParser, ProjectParser
from core.model import WindowSpecs, Scene, Asset, Project
from core.registers import Registry
from core.managers import ProjectPaths
from pathlib import Path

@pytest.fixture
def project_paths(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.assets_dir.mkdir(parents=True, exist_ok=True)
    paths.assets_files_dir.mkdir(parents=True, exist_ok=True)
    paths.entities_dir.mkdir(parents=True, exist_ok=True)
    paths.scenes_dir.mkdir(parents=True, exist_ok=True)
    paths.script_dir.mkdir(parents=True, exist_ok=True)
    return paths

def setup_project(paths: ProjectPaths):
    (paths.assets_dir / "sprite.json").write_text(json.dumps(
        {"unique_name": "sprite", "path": "assets/sprite.jpg"}
    ), encoding="utf-8")
    (paths.entities_dir / "meu_buneco.json").write_text(json.dumps({
        "unique_name": "meu_buneco", "sprite_name": "sprite",
        "width": 5, "height": 10, "script_path": "scripts/buneco.py",
        "variables": {"vida": 100}, "hooks": {"on_spawn": "inicializar"},
    }), encoding="utf-8")
    (paths.scenes_dir / "level01.json").write_text(json.dumps({
        "unique_name": "level01", "background": "sprite",
        "entities": [{"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}],
    }), encoding="utf-8")
    paths.project_file.write_text(json.dumps({
        "name": "Caogeon Demo", "engine_version": "1.0.0",
        "window": {"title": "Janela", "width": 800, "height": 600, "target_fps": 60},
        "initial_scene_name": "level01",
    }), encoding="utf-8")

# --- WindowSpecsParser ---

def test_window_roundtrip():
    original = WindowSpecs(title="Janela", width=800, height=600, target_fps=60)
    parser = WindowSpecsParser()
    assert parser.from_dict(parser.to_dict(original)) == original

# --- ProjectParser ---

def test_project_parser_resolves_scene():
    scenes = Registry()
    scene = Scene(unique_name="level01", background=Asset("bg", Path("bg.jpg")), entities=[])
    scenes.register("level01", scene)
    parser = ProjectParser(WindowSpecsParser(), scenes)
    data = {
        "name": "Demo", "engine_version": "1.0.0",
        "window": {"title": "J", "width": 800, "height": 600, "target_fps": 60},
        "initial_scene_name": "level01",
    }
    project = parser.from_dict(data)
    assert project.initial_scene is scene

# --- ProjectManager ---

def test_project_is_none_before_load():
    assert ProjectManager().project is None

def test_load_populates_project(project_paths):
    setup_project(project_paths)
    manager = ProjectManager()
    manager.load(project_paths)
    assert manager.project is not None
    assert manager.project.name == "Caogeon Demo"

def test_load_populates_all_registries(project_paths):
    setup_project(project_paths)
    manager = ProjectManager()
    manager.load(project_paths)
    assert manager.asset_manager.assets.get("sprite") is not None
    assert manager.entity_manager.entities.get("meu_buneco") is not None
    assert manager.scene_manager.scenes.get("level01") is not None

def test_load_cross_references(project_paths):
    setup_project(project_paths)
    manager = ProjectManager()
    manager.load(project_paths)
    entity = manager.entity_manager.entities.get("meu_buneco")
    assert entity.sprite.unique_name == "sprite" 

def test_save_creates_all_files(project_paths):
    setup_project(project_paths)
    manager = ProjectManager()
    manager.load(project_paths)
    manager.save(project_paths)

    assert (project_paths.assets_dir / "sprite.json").exists()
    assert (project_paths.entities_dir / "meu_buneco.json").exists()
    assert (project_paths.scenes_dir / "level01.json").exists()
    assert project_paths.project_file.exists()

def test_save_and_load_roundtrip(project_paths):
    setup_project(project_paths)
    manager = ProjectManager()
    manager.load(project_paths)
    original_project = manager.project

    manager.save(project_paths)

    manager2 = ProjectManager()
    manager2.load(project_paths)
    assert manager2.project == original_project
