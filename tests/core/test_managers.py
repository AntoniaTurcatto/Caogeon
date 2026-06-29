from typing import cast

import pytest
from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.project_manager import ProjectManager
from core.scene_manager import SceneManager
from core.managers import ProjectPaths, ProjectPathsState
from core.model import Asset, Entity, Project, Scene
from core.serializers import JSONSerializer

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_project(tmp_path) -> ProjectPaths:
    return ProjectPaths(tmp_path)

@pytest.fixture
def state(tmp_project) -> ProjectPathsState:
    s = ProjectPathsState()
    s.project_paths = tmp_project
    return s

@pytest.fixture
def serializer():
    return JSONSerializer()


# ---------------------------------------------------------------------------
# AssetManager fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def asset_manager(state, serializer, tmp_project):
    mgr = AssetManager(state, serializer)
    mgr.new(tmp_project)
    return mgr

@pytest.fixture
def asset1(tmp_project):
    return Asset(unique_name="asset1", path=tmp_project.assets_files_dir / "asset1.png")

@pytest.fixture
def asset2(tmp_project):
    return Asset(unique_name="asset2", path=tmp_project.assets_files_dir / "asset2.png")

@pytest.fixture
def asset3(tmp_project):
    return Asset(unique_name="asset3", path=tmp_project.assets_files_dir / "asset3.png")

@pytest.fixture
def asset_manager_with_assets(asset_manager, asset1, asset2, asset3):
    asset_manager.add(asset1)
    asset_manager.add(asset2)
    asset_manager.add(asset3)
    return asset_manager

# ---------------------------------------------------------------------------
# EntityManager fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def entity_manager(state, serializer, asset_manager_with_assets, tmp_project):
    mgr = EntityManager(state, serializer, asset_manager_with_assets.assets)
    mgr.new(tmp_project)# cria entities_dir
    return mgr

@pytest.fixture
def entity1(tmp_project, asset1):
    return Entity(
        unique_name="entity1",
        sprite=asset1,
        width=50, height=50,
        script_path=tmp_project.entities_script_dir / "entity1.py",
        variables={}, hooks={}
    )

@pytest.fixture
def entity2(tmp_project, asset1):
    return Entity(
        unique_name="entity2",
        sprite=asset1,
        width=32, height=32,
        script_path=tmp_project.entities_script_dir / "entity2.py",
        variables={}, hooks={}
    )


# ---------------------------------------------------------------------------
# SceneManager fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scene_manager(state, serializer, asset_manager, entity_manager, tmp_project):
    mgr = SceneManager(state, serializer, asset_manager.assets, entity_manager.entities)
    mgr.new(tmp_project)   # cria scenes_dir
    return mgr

@pytest.fixture
def scene1(tmp_project):
    return Scene(
        unique_name="scene1",
        background=None,
        entities=[],
        script_path=tmp_project.scenes_script_dir / "scene1.py"
    )


# ---------------------------------------------------------------------------
# AssetManager — add / remove
# ---------------------------------------------------------------------------

def test_asset_add_single(asset_manager, asset1):
    asset_manager.add(asset1)
    assert asset_manager.assets.try_get("asset1") is asset1

def test_asset_add_multiple(asset_manager, asset1, asset2, asset3):
    for a in [asset1, asset2, asset3]:
        asset_manager.add(a)
    assert len(asset_manager.assets.all()) == 3

def test_asset_remove(asset_manager, asset1):
    asset_manager.add(asset1)
    asset_manager.remove("asset1")
    assert asset_manager.assets.try_get("asset1") is None

def test_asset_remove_nonexistent_raises(asset_manager):
    with pytest.raises(KeyError):
        asset_manager.remove("nao_existe")


# ---------------------------------------------------------------------------
# AssetManager — save / load
# ---------------------------------------------------------------------------

def test_asset_save_creates_dir(asset_manager, asset1, tmp_project):
    asset_manager.add(asset1)
    asset_manager.save(tmp_project)
    assert tmp_project.assets_dir.exists()

def test_asset_save_creates_file(asset_manager, asset1, tmp_project):
    asset_manager.add(asset1)
    asset_manager.save(tmp_project)
    assert (tmp_project.assets_dir / "asset1.json").exists()

def test_asset_save_multiple(asset_manager, asset1, asset2, asset3, tmp_project):
    for a in [asset1, asset2, asset3]:
        asset_manager.add(a)
    asset_manager.save(tmp_project)
    assert len(list(tmp_project.assets_dir.glob("*.json"))) == 3

def test_asset_load_empty_dir(asset_manager, tmp_project):
    tmp_project.assets_dir.mkdir(parents=True, exist_ok=True)
    asset_manager.load(tmp_project)
    assert asset_manager.assets.all() == []

def test_asset_load_single(asset_manager, asset1, tmp_project, state, serializer):
    asset_manager.add(asset1)
    asset_manager.save(tmp_project)
    manager2 = AssetManager(state, serializer)
    manager2.load(tmp_project)
    assert manager2.assets.try_get("asset1") == asset1

def test_asset_load_preserves_external_reference(asset_manager, asset1, tmp_project):
    ref = asset_manager.assets
    asset_manager.add(asset1)
    asset_manager.save(tmp_project)
    asset_manager.load(tmp_project)
    assert ref is asset_manager.assets
    assert ref.try_get("asset1") is not None

def test_asset_roundtrip(asset_manager, asset1, asset2, tmp_project, state, serializer):
    asset_manager.add(asset1)
    asset_manager.add(asset2)
    asset_manager.save(tmp_project)
    manager2 = AssetManager(state, serializer)
    manager2.load(tmp_project)
    assert manager2.assets.try_get("asset1") == asset1
    assert manager2.assets.try_get("asset2") == asset2


# ---------------------------------------------------------------------------
# EntityManager — save / load
# ---------------------------------------------------------------------------

def test_entity_save_creates_dir(entity_manager, entity1, tmp_project):
    entity_manager.add(entity1)
    entity_manager.save(tmp_project)
    assert tmp_project.entities_dir.exists()

def test_entity_save_creates_file(entity_manager, entity1, tmp_project):
    entity_manager.add(entity1)
    entity_manager.save(tmp_project)
    assert (tmp_project.entities_dir / "entity1.json").exists()

def test_entity_load_preserves_external_reference(entity_manager, entity1, tmp_project):
    ref = entity_manager.entities
    entity_manager.add(entity1)
    entity_manager.save(tmp_project)
    entity_manager.load(tmp_project)
    assert ref is entity_manager.entities
    assert ref.try_get("entity1") is not None

def test_entity_roundtrip(entity_manager, entity1, entity2, tmp_project, state, serializer, asset_manager_with_assets):
    entity_manager.add(entity1)
    entity_manager.add(entity2)
    entity_manager.save(tmp_project)
    manager2 = EntityManager(state, serializer, asset_manager_with_assets.assets)
    manager2.load(tmp_project)
    assert manager2.entities.try_get("entity1") == entity1
    assert manager2.entities.try_get("entity2") == entity2


# ---------------------------------------------------------------------------
# SceneManager — save / load
# ---------------------------------------------------------------------------

def test_scene_save_creates_dir(scene_manager, scene1, tmp_project):
    scene_manager.scenes.register(scene1.unique_name, scene1)
    scene_manager.save(tmp_project)
    assert tmp_project.scenes_dir.exists()

def test_scene_save_creates_file(scene_manager, scene1, tmp_project):
    scene_manager.scenes.register(scene1.unique_name, scene1)
    scene_manager.save(tmp_project)
    assert (tmp_project.scenes_dir / "scene1.json").exists()

def test_scene_load_preserves_external_reference(scene_manager, scene1, tmp_project):
    ref = scene_manager.scenes
    scene_manager.scenes.register(scene1.unique_name, scene1)
    scene_manager.save(tmp_project)
    scene_manager.load(tmp_project)
    assert ref is scene_manager.scenes
    assert ref.try_get("scene1") is not None

def test_scene_create_blank(scene_manager, tmp_project):
    scene_manager.new(tmp_project)
    scene = scene_manager.create()
    assert scene.unique_name in [s.unique_name for s in scene_manager.scenes.all()]
    assert scene.script_path.exists()

def test_scene_roundtrip(scene_manager, scene1, tmp_project, state, serializer, asset_manager_with_assets, entity_manager):
    scene_manager.scenes.register(scene1.unique_name, scene1)
    scene_manager.save(tmp_project)
    manager2 = SceneManager(state, serializer, asset_manager_with_assets.assets, entity_manager.entities)
    manager2.load(tmp_project)
    assert manager2.scenes.try_get("scene1") == scene1


# ---------------------------------------------------------------------------
# AssetManager — import_asset
# ---------------------------------------------------------------------------

def test_import_asset(asset_manager, tmp_path):
    fake_file = tmp_path / "sprite.png"
    fake_file.touch()
    asset_manager.import_asset(fake_file)
    assert asset_manager.assets.try_get("sprite") is not None

def test_import_asset_uses_stem_as_name(asset_manager, tmp_path):
    fake_file = tmp_path / "my_sprite.png"
    fake_file.touch()
    asset_manager.import_asset(fake_file)
    assert asset_manager.assets.try_get("my_sprite") is not None


# ---------------------------------------------------------------------------
# EntityManager — create
# ---------------------------------------------------------------------------

def test_entity_create(entity_manager, asset1, tmp_project):
    tmp_project.entities_script_dir.mkdir(parents=True, exist_ok=True)
    entity = entity_manager.create(asset1)
    assert entity is not None
    assert entity.sprite is asset1
    assert entity.script_path.exists()

def test_entity_create_without_project_paths(state, serializer, asset_manager_with_assets, asset1):
    state.project_paths = None
    manager = EntityManager(state, serializer, asset_manager_with_assets.assets)
    entity = manager.create(asset1)
    assert entity is None


# ---------------------------------------------------------------------------
# update_property
# ---------------------------------------------------------------------------

def test_update_property_changes_value(asset_manager, asset1):
    asset_manager.add(asset1)
    from core.model import PropertyChange
    change = PropertyChange(asset1, "unique_name", "new_name")
    asset_manager.update_property(change)
    assert asset1.unique_name == "new_name"

def test_update_property_invalid_property_raises(asset_manager, asset1):
    asset_manager.add(asset1)
    from core.model import PropertyChange
    change = PropertyChange(asset1, "nonexistent", "value")
    with pytest.raises(ValueError):
        asset_manager.update_property(change)

def test_update_property_wrong_type_raises(asset_manager, asset1):
    asset_manager.add(asset1)
    from core.model import PropertyChange
    change = PropertyChange(asset1, "unique_name", 123)  # str esperado
    with pytest.raises(ValueError):
        asset_manager.update_property(change)

def test_update_property_id_triggers_listener(asset_manager, asset1):
    asset_manager.add(asset1)
    from core.model import PropertyChange
    calls = []
    asset_manager.add_listener_id_updated(lambda obj, old_id: calls.append((obj, old_id)))
    change = PropertyChange(asset1, "unique_name", "renamed")
    asset_manager.update_property(change)
    assert len(calls) == 1
    assert calls[0][1] == "asset1"
    assert calls[0][0].unique_name == "renamed"

def test_update_property_non_id_does_not_trigger_listener(asset_manager, asset1):
    asset_manager.add(asset1)
    from core.model import PropertyChange
    calls = []
    asset_manager.add_listener_id_updated(lambda obj, old_id: calls.append((obj, old_id)))
    change = PropertyChange(asset1, "path", asset1.path)
    asset_manager.update_property(change)
    assert len(calls) == 0


# ---------------------------------------------------------------------------
# ProjectManager — new / save / load
# ---------------------------------------------------------------------------

@pytest.fixture
def project_manager():
    from core.project_manager import ProjectManager
    return ProjectManager()

def test_project_new_creates_structure(project_manager, tmp_path):
    paths = ProjectPaths(tmp_path)
    project_manager.new(paths, "MyGame")
    assert paths.project_file.exists()
    assert paths.assets_dir.exists()
    assert paths.entities_dir.exists()
    assert paths.scenes_dir.exists()

def test_project_new_creates_initial_scene(project_manager, tmp_path):
    paths = ProjectPaths(tmp_path)
    project_manager.new(paths, "MyGame")
    assert project_manager.project.initial_scene is not None
    assert len(project_manager.scene_manager.scenes.all()) == 1

def test_project_new_sets_name(project_manager, tmp_path):
    paths = ProjectPaths(tmp_path)
    project_manager.new(paths, "MyGame")
    assert project_manager.project.name == "MyGame"

def test_project_save_and_load_roundtrip(project_manager, tmp_path):
    paths = ProjectPaths(tmp_path)
    project_manager.new(paths, "MyGame")
    project_manager.asset_manager.add(
        Asset(unique_name="spr", path=paths.assets_files_dir / "spr.png")
    )
    project_manager.save()

    manager2 = ProjectManager()
    manager2.load(paths)
    assert cast(Project,manager2.project).name == "MyGame"
    assert manager2.asset_manager.assets.try_get("spr") is not None

def test_project_loaded_false_initially(project_manager):
    assert not project_manager.project_loaded()

def test_project_loaded_true_after_new(project_manager, tmp_path):
    project_manager.new(ProjectPaths(tmp_path), "MyGame")
    assert project_manager.project_loaded()

def test_project_save_without_paths_does_nothing(project_manager):
    # não deve lançar exceção
    project_manager.save()

def test_project_import_asset_without_project_raises(project_manager, tmp_path):
    with pytest.raises(ValueError):
        project_manager.import_asset(tmp_path / "sprite.png")
