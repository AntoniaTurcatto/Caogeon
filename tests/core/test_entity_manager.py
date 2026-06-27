import json
import pytest
from pathlib import Path
from core.entity_manager import EntityManager, EntityParser
from core.asset_manager import AssetManager
from core.model import Asset, Entity
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
    return Asset(unique_name="sprite", path=project_paths.assets_files_dir / "sprite.png")

@pytest.fixture
def assets(asset):
    r = Registry()
    r.register(asset.unique_name, asset)
    return r

@pytest.fixture
def parser(assets):
    return EntityParser(assets)

@pytest.fixture
def manager(serializer, assets):
    return EntityManager(serializer, assets)

@pytest.fixture
def entity1(asset):
    return Entity(
        unique_name="entity1", sprite=asset,
        width=5, height=10, script_path=Path("scripts/entity1.py"),
        variables={"vida": 100}, hooks={"on_spawn": "inicializar"},
    )

@pytest.fixture
def entity2(asset):
    return Entity(
        unique_name="entity2", sprite=asset,
        width=8, height=12, script_path=Path("scripts/entity2.py"),
        variables={"vida": 50}, hooks={"on_click": "ao_clicar"},
    )

# --- EntityParser ---

def test_parser_to_dict_serializes_sprite_as_name(parser, entity1):
    result = parser.to_dict(entity1)
    assert result["sprite_name"] == "sprite"

def test_parser_from_dict_resolves_asset(parser, asset):
    data = {
        "unique_name": "entity1", "sprite_name": "sprite",
        "width": 5, "height": 10, "script_path": "scripts/entity1.py",
        "variables": {"vida": 100}, "hooks": {"on_spawn": "inicializar"},
    }
    entity = parser.from_dict(data)
    assert entity.sprite is asset

def test_parser_from_dict_unknown_asset_raises(parser):
    data = {
        "unique_name": "x", "sprite_name": "nao_existe",
        "width": 1, "height": 1, "script_path": "",
        "variables": {}, "hooks": {},
    }
    with pytest.raises(KeyError):
        parser.from_dict(data)

def test_parser_roundtrip(parser, entity1):
    assert parser.from_dict(parser.to_dict(entity1)) == entity1

def test_parser_sees_late_registered_asset():
    assets = Registry()
    parser = EntityParser(assets)
    late_asset = Asset(unique_name="chegou_depois", path=Path("x.png"))
    assets.register(late_asset.unique_name, late_asset)
    data = {
        "unique_name": "x", "sprite_name": "chegou_depois",
        "width": 1, "height": 1, "script_path": "",
        "variables": {}, "hooks": {},
    }
    assert parser.from_dict(data).sprite is late_asset

# --- EntityManager.add ---

def test_add_single(manager, entity1):
    manager.add(entity1)
    assert manager.entities.get("entity1") is entity1

# --- EntityManager.remove ---

def test_remove(manager, entity1):
    manager.add(entity1)
    manager.remove("entity1")
    with pytest.raises(KeyError):
        manager.entities.get("entity1")

# --- EntityManager.save ---

def test_save_creates_file(manager, entity1, project_paths):
    manager.add(entity1)
    manager.save(project_paths)
    assert (project_paths.entities_dir / "entity1.json").exists()

def test_save_serializes_sprite_as_name(manager, entity1, project_paths):
    manager.add(entity1)
    manager.save(project_paths)
    raw = json.loads((project_paths.entities_dir / "entity1.json").read_text())
    assert raw["sprite_name"] == "sprite"
    assert "path" not in raw

# --- EntityManager.load ---

def test_load_empty_dir(manager, project_paths):
    project_paths.entities_dir.mkdir(parents=True, exist_ok=True)
    manager.load(project_paths)
    assert manager.entities.all() == []

def test_load_maintains_external_reference(manager, entity1, project_paths):
    external_ref = manager.entities
    manager.add(entity1)
    manager.save(project_paths)
    manager.load(project_paths)
    assert external_ref is manager.entities
    assert external_ref.get("entity1") is not None

# --- save/load roundtrip ---

def test_save_load_roundtrip(manager, entity1, entity2, project_paths, assets):
    manager.add(entity1)
    manager.add(entity2)
    manager.save(project_paths)

    manager2 = EntityManager(JSONSerializer(), assets)
    manager2.load(project_paths)
    assert manager2.entities.get("entity1") == entity1
    assert manager2.entities.get("entity2") == entity2
