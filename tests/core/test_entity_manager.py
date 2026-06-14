import pytest
from pathlib import Path
from core.entity_manager import EntityManager, EntityParser
from core.managers import ProjectPaths
from core.serializers import JSONSerializer
from core.registers import Registry
from core.model import Asset, Entity

@pytest.fixture
def asset():
    return Asset(unique_name="imagem_legal", path=Path("assets/img.jpg"))

@pytest.fixture
def assets(asset):
    registry = Registry[Asset]()
    registry.register(asset.unique_name, asset)
    return registry

@pytest.fixture
def parser(assets):
    return EntityParser(assets)

@pytest.fixture
def entity(asset):
    return Entity(
        unique_name="meu_buneco",
        sprite=asset,
        width=5,
        height=10,
        script_path=Path("scripts/script.py"),
        variables={"vida": 100},
        hooks={"on_spawn": "inicializar"},
    )

@pytest.fixture
def project_paths(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.entities_dir.mkdir(parents=True, exist_ok=True)
    return paths

# --- EntityParser ---

def test_to_dict(parser, entity):
    result = parser.to_dict(entity)
    assert result["sprite_name"] == "imagem_legal" 
    assert result["unique_name"] == "meu_buneco"

def test_from_dict_resolves_asset(parser, asset):
    data = {
        "unique_name": "meu_buneco",
        "sprite_name": "imagem_legal",
        "width": 5,
        "height": 10,
        "script_path": "scripts/script.py",
        "variables": {"vida": 100},
        "hooks": {"on_spawn": "inicializar"},
    }
    entity = parser.from_dict(data)
    assert entity.sprite is asset 

def test_from_dict_unknown_asset_raises(parser):
    data = {"sprite_name": "nao_existe", "unique_name": "x",
            "width": 1, "height": 1, "script_path": "", "variables": {}, "hooks": {}}
    with pytest.raises(KeyError):
        parser.from_dict(data)

def test_roundtrip(parser, entity):
    assert parser.from_dict(parser.to_dict(entity)) == entity

# --- Registry atualizado depois é enxergado ---

def test_registry_late_register():
    assets = Registry[Asset]()
    parser = EntityParser(assets) 

    late_asset = Asset(unique_name="chegou_depois", path=Path("x.jpg"))
    assets.register(late_asset.unique_name, late_asset) 

    data = {"unique_name": "x", "sprite_name": "chegou_depois",
            "width": 1, "height": 1, "script_path": "", "variables": {}, "hooks": {}}
    entity = parser.from_dict(data)
    assert entity.sprite is late_asset

def test_save_single(project_paths, assets, entity):
    manager = EntityManager(JSONSerializer(), assets)
    manager.entities.register(entity.unique_name, entity)
    manager.save(project_paths)
    assert (project_paths.entities_dir / "meu_buneco.json").exists()

def test_save_creates_dir(tmp_path, assets, entity):
    paths = ProjectPaths(tmp_path)
    manager = EntityManager(JSONSerializer(), assets)
    manager.entities.register(entity.unique_name, entity)
    manager.save(paths)
    assert paths.entities_dir.exists()

def test_save_and_load_roundtrip(project_paths, assets, entity):
    manager = EntityManager(JSONSerializer(), assets)
    manager.entities.register(entity.unique_name, entity)
    manager.save(project_paths)

    manager2 = EntityManager(JSONSerializer(), assets)
    manager2.load(project_paths)
    assert manager2.entities.get(entity.unique_name) == entity

def test_save_serializes_sprite_as_name(project_paths, assets, entity):
    """garante que to_dict não serializa o objeto Asset, mas o unique_name"""
    manager = EntityManager(JSONSerializer(), assets)
    manager.entities.register(entity.unique_name, entity)
    manager.save(project_paths)

    import json
    raw = json.loads((project_paths.entities_dir / "meu_buneco.json").read_text())
    assert raw["sprite_name"] == "imagem_legal"
    assert "path" not in raw  # objeto Asset não deve vazar no JSON
