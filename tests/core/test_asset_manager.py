import pytest
from pathlib import Path
from core.asset_manager import AssetManager, AssetParser
from core.serializers import JSONSerializer
from core.model import Asset

@pytest.fixture
def parser():
    return AssetParser()

@pytest.fixture
def json_serializer():
    return JSONSerializer()

# --- AssetParser ---

def test_to_dict(parser):
    asset = Asset(unique_name="imagem legal", path=Path("assets/img.jpg"))
    assert parser.to_dict(asset) == {
        "unique_name": "imagem legal",
        "path": "assets/img.jpg"
    }

def test_from_dict(parser):
    data = {"unique_name": "imagem legal", "path": "assets/img.jpg"}
    asset = parser.from_dict(data)
    assert asset.unique_name == "imagem legal"
    assert asset.path == Path("assets/img.jpg")

def test_from_dict_missing_path_raises(parser):
    with pytest.raises(KeyError):
        parser.from_dict({"unique_name": "imagem legal"})

def test_roundtrip(parser):
    original = Asset(unique_name="imagem legal", path=Path("assets/img.jpg"))
    assert parser.from_dict(parser.to_dict(original)) == original

# --- JSONSerializer ---

def test_json_serialize(json_serializer):
    data = {"unique_name": "imagem legal", "path": "assets/img.jpg"}
    text = json_serializer.serialize(data)
    assert json_serializer.deserialize(text) == data

# --- DataSerializer (integração parser + serializer) ---

def test_save_and_load(tmp_path, parser, json_serializer):
    from core.serializers import DataSerializer
    filepath = tmp_path / "imagem_legal.json"
    asset = Asset(unique_name="imagem legal", path=filepath)
    serializer = DataSerializer(parser, json_serializer)
    serializer.save_to_file(asset, filepath)
    loaded = serializer.load_from_file(filepath)
    assert loaded == asset

def test_load_nonexistent_raises(tmp_path, parser, json_serializer):
    from core.serializers import DataSerializer
    serializer = DataSerializer(parser, json_serializer)
    with pytest.raises(FileNotFoundError):
        serializer.load_from_file(tmp_path / "nao_existe.json")

# --- AssetManager ---

@pytest.fixture
def project_paths(tmp_path):
    from core.managers import ProjectPaths
    return ProjectPaths(tmp_path)

def test_clean_assets_creates_folders(project_paths):
    manager = AssetManager(project_paths, JSONSerializer())
    manager.clean_assets()
    assert project_paths.assets_dir.exists()
    assert project_paths.assets_files_dir.exists()

def test_clean_assets_removes_existing(project_paths):
    manager = AssetManager(project_paths, JSONSerializer())
    manager.clean_assets()
    (project_paths.assets_dir / "lixo.json").write_text("{}")
    manager.clean_assets()
    assert list(project_paths.assets_dir.iterdir()) == []
