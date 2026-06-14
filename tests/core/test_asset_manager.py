import pytest
from core.asset_manager import AssetManager, AssetParser
from core.model import Asset
from core.managers import ProjectPaths
from core.serializers import JSONSerializer

@pytest.fixture
def project_paths(tmp_path):
    return ProjectPaths(tmp_path)

@pytest.fixture
def parser():
    return AssetParser()

@pytest.fixture
def serializer():
    return JSONSerializer()

@pytest.fixture
def manager(serializer):
    return AssetManager(serializer)

@pytest.fixture
def asset1(project_paths):
    return Asset(unique_name="asset1", path=project_paths.assets_files_dir / "asset1.png")

@pytest.fixture
def asset2(project_paths):
    return Asset(unique_name="asset2", path=project_paths.assets_files_dir / "asset2.png")

@pytest.fixture
def asset3(project_paths):
    return Asset(unique_name="asset3", path=project_paths.assets_files_dir / "asset3.png")

# --- AssetParser ---

def test_parser_to_dict(parser, asset1):
    result = parser.to_dict(asset1)
    assert result["unique_name"] == "asset1"
    assert "path" in result

def test_parser_from_dict(parser, project_paths):
    data = {"unique_name": "asset1", "path": str(project_paths.assets_files_dir / "asset1.png")}
    asset = parser.from_dict(data)
    assert asset.unique_name == "asset1"

def test_parser_from_dict_missing_field_raises(parser):
    with pytest.raises(KeyError):
        parser.from_dict({"unique_name": "asset1"})

def test_parser_roundtrip(parser, asset1):
    assert parser.from_dict(parser.to_dict(asset1)) == asset1

# --- AssetManager.add ---

def test_add_single(manager, asset1):
    manager.add(asset1)
    assert manager.assets.get("asset1") is asset1

def test_add_multiple(manager, asset1, asset2, asset3):
    manager.add(asset1)
    manager.add(asset2)
    manager.add(asset3)
    assert len(manager.assets.all()) == 3

def test_add_duplicate_raises(manager, asset1):
    manager.add(asset1)
    with pytest.raises(KeyError):
        manager.add(asset1)

# --- AssetManager.remove ---

def test_remove(manager, asset1):
    manager.add(asset1)
    manager.remove("asset1")
    with pytest.raises(KeyError):
        manager.assets.get("asset1")

def test_remove_nonexistent_raises(manager):
    with pytest.raises(KeyError):
        manager.remove("nao_existe")

# --- AssetManager.save ---

def test_save_creates_dir(manager, asset1, project_paths):
    manager.add(asset1)
    manager.save(project_paths)
    assert project_paths.assets_dir.exists()

def test_save_creates_file(manager, asset1, project_paths):
    manager.add(asset1)
    manager.save(project_paths)
    assert (project_paths.assets_dir / "asset1.json").exists()

def test_save_multiple(manager, asset1, asset2, asset3, project_paths):
    manager.add(asset1)
    manager.add(asset2)
    manager.add(asset3)
    manager.save(project_paths)
    assert len(list(project_paths.assets_dir.glob("*.json"))) == 3

# --- AssetManager.load ---

def test_load_empty_dir(manager, project_paths):
    project_paths.assets_dir.mkdir(parents=True, exist_ok=True)
    manager.load(project_paths)
    assert manager.assets.all() == []

def test_load_single(manager, asset1, project_paths):
    manager.add(asset1)
    manager.save(project_paths)

    manager2 = AssetManager(JSONSerializer())
    manager2.load(project_paths)
    assert manager2.assets.get("asset1") == asset1

def test_load_maintains_external_reference(manager, asset1, project_paths):
    external_ref = manager.assets
    manager.add(asset1)
    manager.save(project_paths)
    manager.load(project_paths)
    assert external_ref is manager.assets
    assert external_ref.get("asset1") is not None

# --- save/load roundtrip ---

def test_save_load_roundtrip(manager, asset1, asset2, project_paths):
    manager.add(asset1)
    manager.add(asset2)
    manager.save(project_paths)

    manager2 = AssetManager(JSONSerializer())
    manager2.load(project_paths)
    assert manager2.assets.get("asset1") == asset1
    assert manager2.assets.get("asset2") == asset2
