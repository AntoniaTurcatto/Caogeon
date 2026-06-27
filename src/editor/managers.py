from typing import Callable

from PySide6.QtCore import Slot

from core.model import Asset, Entity, ProjectPartBase, PropertyChange, Scene
from core.project_manager import ProjectManager
from editor.panels.inspectors import GenericInspectorPanel
from editor.panels.panels import BrowserPanel

class EditorManager:
  """A manager for the editor state, manages the state of the editor and its panels.
  Binds the project manager, inspector, and asset panel together and its Signals and slots."""

  def __init__(self,
      proj_manager: ProjectManager,
      inspector: GenericInspectorPanel,
      asset_panel: BrowserPanel,
      scene_panel: BrowserPanel,
      entity_panel: BrowserPanel,
  ):
    self.proj_manager = proj_manager
    self.inspector = inspector
    self.asset_panel = asset_panel
    self.scene_panel = scene_panel
    self.entity_panel = entity_panel
    self.map_inspect_strategy: dict[type[ProjectPartBase], Callable[[PropertyChange], None]] = {}
    self.bind_events()
    self.bind_inspect_strategy()

  def bind_events(self):
    self.bind_selected()
    self.bind_removed()
    self.inspector.property_edited.connect(self.update_property)
    self.bind_property_changed()

  def bind_selected(self):
    self.asset_panel.selected.connect(self.asset_selected)
    self.scene_panel.selected.connect(self.scene_selected)
    self.entity_panel.selected.connect(self.entity_selected)

  def bind_removed(self):
    self.asset_panel.removed.connect(self.asset_removed)
    self.scene_panel.removed.connect(self.scene_removed)
    self.entity_panel.removed.connect(self.entity_removed)

  def bind_id_changed(self):
    self.proj_manager.asset_manager.add_listener_id_updated(lambda asset, old_id: self.asset_panel.update_item_label(old_label=old_id, new_label=asset.unique_name))
    self.proj_manager.entity_manager.add_listener_id_updated(lambda entity, old_id: self.entity_panel.update_item_label(old_label=old_id, new_label=entity.unique_name))
    self.proj_manager.scene_manager.add_listener_id_updated(lambda scene, old_id: self.scene_panel.update_item_label(old_label=old_id, new_label=scene.unique_name))

  def bind_property_changed(self):
    self.proj_manager.asset_manager.assets.on_change.append(
      lambda: self.asset_panel.load_assets(
        [a.unique_name for a in self.proj_manager.asset_manager.assets.as_list()]
      )
    )
    self.proj_manager.entity_manager.entities.on_change.append(
      lambda: self.entity_panel.load_assets(
        [e.unique_name for e in self.proj_manager.entity_manager.entities.as_list()]
      )
    )
    self.proj_manager.scene_manager.scenes.on_change.append(
      lambda: self.scene_panel.load_assets(
        [s.unique_name for s in self.proj_manager.scene_manager.scenes.as_list()]
      )
    )

  def bind_inspect_strategy(self):
    self.map_inspect_strategy[Asset] = self.proj_manager.asset_manager.update_property
    self.map_inspect_strategy[Scene] = self.proj_manager.scene_manager.update_property
    self.map_inspect_strategy[Entity] = self.proj_manager.entity_manager.update_property

  @Slot(str)
  def asset_selected(self, asset_id):
    asset = self.proj_manager.asset_manager.get(asset_id)
    if asset is not None:
      self.inspector.inspect(asset)

  @Slot(str)
  def scene_selected(self, scene_id):
    scene = self.proj_manager.scene_manager.get(scene_id)
    if scene is not None:
      self.inspector.inspect(scene)

  @Slot(str)
  def entity_selected(self, entity_id):
    entity = self.proj_manager.entity_manager.get(entity_id)
    if entity is not None:
      self.inspector.inspect(entity)

  @Slot(str)
  def asset_removed(self, asset_id):
    self.proj_manager.asset_manager.assets.unregister(asset_id)

  @Slot(str)
  def scene_removed(self, scene_id):
    self.proj_manager.scene_manager.scenes.unregister(scene_id)

  @Slot(str)
  def entity_removed(self, entity_id):
    self.proj_manager.entity_manager.entities.unregister(entity_id)

  @Slot(PropertyChange)
  def update_property(self, change: PropertyChange):
    self.map_inspect_strategy[type(change.obj)](change)
