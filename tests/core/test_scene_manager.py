import json
import pytest
from pathlib import Path
from core.scene_manager import SceneManager, SceneParser, InstancedEntityParser
from core.model import Asset, Entity, InstancedEntity, Scene
from core.registers import Registry
from core.managers import ProjectPaths
from core.serializers import JSONSerializer

@pytest.fixture
def asset():
    return Asset(unique_name="bg", path=Path("assets/bg.jpg"))

@pytest.fixture
def assets(asset):
    r = Registry()
    r.register(asset.unique_name, asset)
    return r

@pytest.fixture
def entity(asset):
    return Entity(
        unique_name="meu_buneco", sprite=asset,
        width=5, height=10, script_path=Path("scripts/buneco.py"),
        variables={}, hooks={},
    )

@pytest.fixture
def entities(entity):
    r = Registry()
    r.register(entity.unique_name, entity)
    return r

@pytest.fixture
def scene(asset, entity):
    return Scene(
        unique_name="level01", background=asset,
        entities=[InstancedEntity(id="buneco_1", entity=entity, x=25, y=30)],
    )

@pytest.fixture
def project_paths(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.scenes_dir.mkdir(parents=True, exist_ok=True)
    return paths

# --- InstancedEntityParser ---

def test_instanced_to_dict(entities, entity):
    parser = InstancedEntityParser(entities)
    result = parser.to_dict(InstancedEntity(id="b1", entity=entity, x=25, y=30))
    assert result == {"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}

def test_instanced_from_dict_resolves_entity(entities, entity):
    parser = InstancedEntityParser(entities)
    instanced = parser.from_dict({"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30})
    assert instanced.entity is entity

def test_instanced_from_dict_unknown_entity_raises(entities):
    parser = InstancedEntityParser(entities)
    with pytest.raises(KeyError):
        parser.from_dict({"id": "b1", "entity_name": "nao_existe", "x": 0, "y": 0})

# --- SceneParser ---

def test_scene_to_dict_serializes_background_as_name(assets, entities, scene):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    result = parser.to_dict(scene)
    assert result["background"] == "bg"  # objeto -> referência por nome
    assert len(result["entities"]) == 1

def test_scene_from_dict_resolves_references(assets, entities, asset, entity):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    data = {
        "unique_name": "level01", "background": "bg",
        "entities": [{"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}],
    }
    scene = parser.from_dict(data)
    assert scene.background is asset
    assert scene.entities[0].entity is entity

def test_scene_roundtrip(assets, entities, scene):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    assert parser.from_dict(parser.to_dict(scene)) == scene

# --- SceneManager.load ---

def test_load_single(project_paths, assets, entities):
    data = {
        "unique_name": "level01", "background": "bg",
        "entities": [{"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}],
    }
    (project_paths.scenes_dir / "level01.json").write_text(json.dumps(data), encoding="utf-8")
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.load(project_paths)
    scene = manager.scenes.get("level01")
    assert scene.background.unique_name == "bg"
    assert scene.entities[0].entity.unique_name == "meu_buneco"

def test_load_empty_dir(project_paths, assets, entities):
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.load(project_paths)
    assert manager.scenes.all() == []

def test_save_single(project_paths, assets, entities, scene):
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.scenes.register(scene.unique_name, scene)
    manager.save(project_paths)
    assert (project_paths.scenes_dir / "level01.json").exists()

def test_save_creates_dir(tmp_path, assets, entities, scene):
    paths = ProjectPaths(tmp_path)
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.scenes.register(scene.unique_name, scene)
    manager.save(paths)
    assert paths.scenes_dir.exists()

def test_save_and_load_roundtrip(project_paths, assets, entities, scene):
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.scenes.register(scene.unique_name, scene)
    manager.save(project_paths)

    manager2 = SceneManager(JSONSerializer(), assets, entities)
    manager2.load(project_paths)
    loaded = manager2.scenes.get(scene.unique_name)
    assert loaded == scene

def test_save_serializes_references_as_names(project_paths, assets, entities, scene):
    """garante que background e entity_name são strings, não objetos"""
    manager = SceneManager(JSONSerializer(), assets, entities)
    manager.scenes.register(scene.unique_name, scene)
    manager.save(project_paths)

    import json
    raw = json.loads((project_paths.scenes_dir / "level01.json").read_text())
    assert raw["background"] == "bg"
    assert raw["entities"][0]["entity_name"] == "meu_buneco"
