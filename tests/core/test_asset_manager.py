import json
import pytest
from pathlib import Path
from core.asset_manager import AssetManager, AssetParser
from core.model import Asset
from core.managers import ProjectPaths
from core.serializers import JSONSerializer

@pytest.fixture
def parser():
    return AssetParser()

@pytest.fixture
def asset():
    return Asset(unique_name="sprite", path=Path("assets/sprite.jpg"))

@pytest.fixture
def project_paths(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.assets_dir.mkdir(parents=True, exist_ok=True)
    return paths

def write_json(directory: Path, data: dict):
    (directory / f"{data['unique_name']}.json").write_text(json.dumps(data), encoding="utf-8")

# --- AssetParser ---

def test_to_dict(parser, asset):
    assert parser.to_dict(asset) == {"unique_name": "sprite", "path": "assets/sprite.jpg"}

def test_from_dict(parser):
    asset = parser.from_dict({"unique_name": "sprite", "path": "assets/sprite.jpg"})
    assert asset.unique_name == "sprite"
    assert asset.path == Path("assets/sprite.jpg")

def test_from_dict_missing_field_raises(parser):
    with pytest.raises(KeyError):
        parser.from_dict({"unique_name": "sprite"})

def test_roundtrip(parser, asset):
    assert parser.from_dict(parser.to_dict(asset)) == asset

# --- AssetManager.load ---

def test_load_single(project_paths):
    write_json(project_paths.assets_dir, {"unique_name": "sprite", "path": "assets/sprite.jpg"})
    manager = AssetManager(JSONSerializer())
    manager.load(project_paths)
    assert manager.assets.get("sprite").path == Path("assets/sprite.jpg")

def test_load_multiple(project_paths):
    for i in range(3):
        write_json(project_paths.assets_dir, {"unique_name": f"asset_{i}", "path": f"img_{i}.jpg"})
    manager = AssetManager(JSONSerializer())
    manager.load(project_paths)
    assert len(manager.assets.all()) == 3

def test_load_empty_dir(project_paths):
    manager = AssetManager(JSONSerializer())
    manager.load(project_paths)
    assert manager.assets.all() == []

def test_load_mantains_external_reference(project_paths):
    """load() atualiza o registry existente — referências externas capturadas antes continuam válidas"""
    manager = AssetManager(JSONSerializer())
    external_ref = manager.assets  # captura referência antes do load

    write_json(project_paths.assets_dir, {"unique_name": "sprite", "path": "assets/sprite.jpg"})
    manager.load(project_paths)

    assert external_ref.get("sprite") is not None          # referência externa enxerga os novos dados
    assert external_ref is manager.assets                  # é o mesmo objeto


def test_save_single(project_paths):
    manager = AssetManager(JSONSerializer())
    manager.assets.register("sprite", Asset(unique_name="sprite", path=Path("assets/sprite.jpg")))
    manager.save(project_paths)
    assert (project_paths.assets_dir / "sprite.json").exists()

def test_save_creates_dir(tmp_path):
    paths = ProjectPaths(tmp_path)  # sem mkdir
    manager = AssetManager(JSONSerializer())
    manager.assets.register("sprite", Asset(unique_name="sprite", path=Path("assets/sprite.jpg")))
    manager.save(paths)  # não deve explodir
    assert paths.assets_dir.exists()

def test_save_and_load_roundtrip(project_paths):
    original = Asset(unique_name="sprite", path=Path("assets/sprite.jpg"))
    manager = AssetManager(JSONSerializer())
    manager.assets.register(original.unique_name, original)
    manager.save(project_paths)

    manager2 = AssetManager(JSONSerializer())
    manager2.load(project_paths)
    assert manager2.assets.get("sprite") == original

def test_save_multiple(project_paths):
    manager = AssetManager(JSONSerializer())
    for i in range(3):
        manager.assets.register(f"asset_{i}", Asset(unique_name=f"asset_{i}", path=Path(f"img_{i}.jpg")))
    manager.save(project_paths)
    assert len(list(project_paths.assets_dir.glob("*.json"))) == 3

def test_save_overwrites_existing(project_paths):
    manager = AssetManager(JSONSerializer())
    asset = Asset(unique_name="sprite", path=Path("img_original.jpg"))
    manager.assets.register(asset.unique_name, asset)
    manager.save(project_paths)

    manager.assets.register("sprite", Asset(unique_name="sprite", path=Path("img_novo.jpg")))
    manager.save(project_paths)

    manager2 = AssetManager(JSONSerializer())
    manager2.load(project_paths)
    assert manager2.assets.get("sprite").path == Path("img_novo.jpg")
