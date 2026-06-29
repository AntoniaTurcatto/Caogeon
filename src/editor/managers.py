from typing import Callable

from PySide6.QtCore import Slot

from core.model import Asset, Entity, ProjectPartBase, PropertyChange, Scene
from core.project_manager import ProjectManager
from editor.dialogs.manager import DialogManager
from editor.panels.inspectors import GenericInspectorPanel
from editor.panels.panels import BrowserPanel

class EditorManager:
  """A manager to do the comunication between the project manager, inspector, and project parts browser panels."""

  def __init__(self,
      proj_manager: ProjectManager,
      dialogs_manager: DialogManager,
      inspector: GenericInspectorPanel,
      asset_panel: BrowserPanel,
      scene_panel: BrowserPanel,
      entity_panel: BrowserPanel,
  ):
    self.proj_manager = proj_manager
    self.dialogs_manager = dialogs_manager
    self.inspector = inspector
    self.asset_panel = asset_panel
    self.scene_panel = scene_panel
    self.entity_panel = entity_panel
    self.update_property_strategy: dict[type[ProjectPartBase], Callable[[PropertyChange], None]] = {}
    self.bind_events()
    self.bind_update_strategy()

  def bind_events(self):
    self.bind_selected()
    self.bind_creation_requested()
    self.bind_remove_requested()
    self.bind_id_changed()
    self.inspector.property_edited.connect(self.update_property)
    self.bind_on_registry_change()

  def bind_selected(self):
    """Bind the selection signal of browsers"""
    self.asset_panel.selected.connect(self.asset_selected)
    self.scene_panel.selected.connect(self.scene_selected)
    self.entity_panel.selected.connect(self.entity_selected)

  def bind_creation_requested(self):
    """Bind the creation request signal of browsers"""
    self.scene_panel.create_opc_clicked.connect(self.scene_creation_requested)
    self.entity_panel.create_opc_clicked.connect(self.entity_creation_requested)

  def bind_remove_requested(self):
    """Bind the removal request signal of browsers"""
    self.asset_panel.remove_opc_clicked.connect(self.asset_removal_requested)
    self.scene_panel.remove_opc_clicked.connect(self.scene_removal_requested)
    self.entity_panel.remove_opc_clicked.connect(self.entity_removal_requested)

  def bind_id_changed(self):
    """Bind the ID change signal of project parts to browser update its item labels"""
    self.proj_manager.asset_manager.add_listener_id_updated(lambda asset, old_id: self.asset_panel.update_item_label(old_label=old_id, new_label=asset.unique_name))
    self.proj_manager.entity_manager.add_listener_id_updated(lambda entity, old_id: self.entity_panel.update_item_label(old_label=old_id, new_label=entity.unique_name))
    self.proj_manager.scene_manager.add_listener_id_updated(lambda scene, old_id: self.scene_panel.update_item_label(old_label=old_id, new_label=scene.unique_name))

  def bind_on_registry_change(self):
    """Bind the registry added or removed signal of project parts to browser update its item labels"""

    self.proj_manager.asset_manager.assets.on_add_remove.append(
      lambda: self.asset_panel.load_assets(
        [a.unique_name for a in self.proj_manager.asset_manager.assets.as_list()]
      )
    )
    self.proj_manager.entity_manager.entities.on_add_remove.append(
      lambda: self.entity_panel.load_assets(
        [e.unique_name for e in self.proj_manager.entity_manager.entities.as_list()]
      )
    )
    self.proj_manager.scene_manager.scenes.on_add_remove.append(
      lambda: self.scene_panel.load_assets(
        [s.unique_name for s in self.proj_manager.scene_manager.scenes.as_list()]
      )
    )

  def bind_update_strategy(self):
    """Bind the ProjectPartBase subtype to the adequate update property strategy."""
    self.update_property_strategy[Asset] = self.proj_manager.asset_manager.update_property
    self.update_property_strategy[Scene] = self.proj_manager.scene_manager.update_property
    self.update_property_strategy[Entity] = self.proj_manager.entity_manager.update_property

  @Slot(str)
  def asset_selected(self, asset_id):
    """Inspect the selected asset."""
    asset = self.proj_manager.asset_manager.get(asset_id)
    if asset is not None:
      self.inspector.inspect(asset)

  @Slot(str)
  def scene_selected(self, scene_id):
    """Inspect the selected scene."""
    scene = self.proj_manager.scene_manager.get(scene_id)
    if scene is not None:
      self.inspector.inspect(scene)

  @Slot(str)
  def entity_selected(self, entity_id):
    """Inspect the selected entity."""
    entity = self.proj_manager.entity_manager.get(entity_id)
    if entity is not None:
      self.inspector.inspect(entity)

  @Slot()
  def scene_creation_requested(self):
    """Create a blank scene."""
    self.proj_manager.scene_manager.create()

  @Slot()
  def entity_creation_requested(self):
    """Create a dialog to create an entity."""
    self.dialogs_manager.entity_creation_dialog.show("Create Entity")


  @Slot(str)
  def asset_removal_requested(self, asset_id):
    """Remove an asset."""
    self.proj_manager.asset_manager.remove(asset_id)

  @Slot(str)
  def scene_removal_requested(self, scene_id):
    """Remove a scene."""
    self.proj_manager.scene_manager.remove(scene_id)

  @Slot(str)
  def entity_removal_requested(self, entity_id):
    """Remove an entity."""
    self.proj_manager.entity_manager.remove(entity_id)

  @Slot(PropertyChange)
  def update_property(self, change: PropertyChange):
    """Update the property of the current inspected object, based on its type."""
    self.update_property_strategy[type(change.obj)](change)
