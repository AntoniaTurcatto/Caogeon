import pytest
from pathlib import Path
from core.entity_manager import EntityManager, EntityParser
from core.serializers import JSONSerializer
from core.registers import Registry
from core.model import Asset, Entity

@pytest.fixture
def asset():
    return Asset(unique_name="imagem legal", path=Path("assets/img.jpg"))

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
        unique_name="meu buneco",
        sprite=asset,
        width=5,
        height=10,
        script_path=Path("scripts/script.py"),
        variables={"vida": 100},
        hooks={"on_spawn": "inicializar"},
    )

# --- EntityParser ---

def test_to_dict(parser, entity):
    result = parser.to_dict(entity)
    assert result["sprite_name"] == "imagem legal" 
    assert result["unique_name"] == "meu buneco"

def test_from_dict_resolves_asset(parser, asset):
    data = {
        "unique_name": "meu buneco",
        "sprite_name": "imagem legal",
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
