import json
import pytest
from pathlib import Path
from core.scene_manager import SceneManager, SceneParser, InstancedEntityParser
from core.model import Asset, Entity, InstancedEntity, Scene
from core.registers import Registry
from core.managers import ProjectPaths
from core.serializers import JSONSerializer

@pytest.fixture
def project_paths(tmp_path):
    return ProjectPaths(tmp_path)

@pytest.fixture
def serializer():
    return JSONSerializer()

@pytest.fixture
def asset(project_paths):
    return Asset(unique_name="bg", path=project_paths.assets_files_dir / "bg.png")

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
def manager(serializer, assets, entities):
    return SceneManager(serializer, assets, entities)

@pytest.fixture
def instanced1(entity):
    return InstancedEntity(id="buneco_1", entity=entity, x=25, y=30)

@pytest.fixture
def instanced2(entity):
    return InstancedEntity(id="buneco_2", entity=entity, x=100, y=200)

@pytest.fixture
def scene1(asset, instanced1):
    return Scene(unique_name="level01", background=asset, entities=[instanced1])

@pytest.fixture
def scene2(asset, instanced2):
    return Scene(unique_name="level02", background=asset, entities=[instanced2])

# --- InstancedEntityParser ---

def test_instanced_to_dict(entities, instanced1):
    parser = InstancedEntityParser(entities)
    result = parser.to_dict(instanced1)
    assert result == {"id": "buneco_1", "entity_name": "meu_buneco", "x": 25, "y": 30}

def test_instanced_from_dict_resolves_entity(entities, entity):
    parser = InstancedEntityParser(entities)
    result = parser.from_dict({"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30})
    assert result.entity is entity

def test_instanced_from_dict_unknown_entity_raises(entities):
    parser = InstancedEntityParser(entities)
    with pytest.raises(KeyError):
        parser.from_dict({"id": "b1", "entity_name": "nao_existe", "x": 0, "y": 0})

# --- SceneParser ---

def test_scene_to_dict_serializes_references(assets, entities, scene1):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    result = parser.to_dict(scene1)
    assert result["background"] == "bg"
    assert result["entities"][0]["entity_name"] == "meu_buneco"

def test_scene_from_dict_resolves_references(assets, entities, asset, entity):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    data = {
        "unique_name": "level01", "background": "bg",
        "entities": [{"id": "b1", "entity_name": "meu_buneco", "x": 25, "y": 30}],
    }
    scene = parser.from_dict(data)
    assert scene.background is asset
    assert scene.entities[0].entity is entity

def test_scene_roundtrip(assets, entities, scene1):
    parser = SceneParser(assets, InstancedEntityParser(entities))
    assert parser.from_dict(parser.to_dict(scene1)) == scene1

# --- SceneManager.add ---

def test_add_single(manager, scene1):
    manager.add(scene1)
    assert manager.scenes.get("level01") is scene1

def test_add_duplicate_raises(manager, scene1):
    manager.add(scene1)
    with pytest.raises(KeyError):
        manager.add(scene1)

# --- SceneManager.remove ---

def test_remove(manager, scene1):
    manager.add(scene1)
    manager.remove("level01")
    with pytest.raises(KeyError):
        manager.scenes.get("level01")

# --- SceneManager.save ---

def test_save_creates_file(manager, scene1, project_paths):
    manager.add(scene1)
    manager.save(project_paths)
    assert (project_paths.scenes_dir / "level01.json").exists()

def test_save_serializes_references_as_names(manager, scene1, project_paths):
    manager.add(scene1)
    manager.save(project_paths)
    raw = json.loads((project_paths.scenes_dir / "level01.json").read_text())
    assert raw["background"] == "bg"
    assert raw["entities"][0]["entity_name"] == "meu_buneco"

# --- SceneManager.load ---

def test_load_empty_dir(manager, project_paths):
    project_paths.scenes_dir.mkdir(parents=True, exist_ok=True)
    manager.load(project_paths)
    assert manager.scenes.all() == []

def test_load_maintains_external_reference(manager, scene1, project_paths):
    external_ref = manager.scenes
    manager.add(scene1)
    manager.save(project_paths)
    manager.load(project_paths)
    assert external_ref is manager.scenes
    assert external_ref.get("level01") is not None

# --- save/load roundtrip ---

def test_save_load_roundtrip(manager, scene1, scene2, project_paths, assets, entities):
    manager.add(scene1)
    manager.add(scene2)
    manager.save(project_paths)

    manager2 = SceneManager(JSONSerializer(), assets, entities)
    manager2.load(project_paths)
    assert manager2.scenes.get("level01") == scene1
    assert manager2.scenes.get("level02") == scene2
