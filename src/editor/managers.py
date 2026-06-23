from enum import Enum

from PySide6.QtCore import Slot

from core.model import ProjectPart
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
    self.bind_events()

  def bind_events(self):
    self.asset_panel.selected.connect(self.asset_selected)
    self.scene_panel.selected.connect(self.scene_selected)
    self.entity_panel.selected.connect(self.entity_selected)
    self.inspector.property_changed.connect(self.update_property)
    self.proj_manager.asset_manager.assets.on_change.append(lambda _: self.asset_panel.load_assets([a.unique_name for a in self.proj_manager.asset_manager.assets.as_list()]))
    self.proj_manager.entity_manager.entities.on_change.append(lambda _: self.entity_panel.load_assets([e.unique_name for e in self.proj_manager.entity_manager.entities.as_list()]))
    self.proj_manager.scene_manager.scenes.on_change.append(lambda _: self.scene_panel.load_assets([s.unique_name for s in self.proj_manager.scene_manager.scenes.as_list()]))

  @Slot(str)
  def asset_selected(self, asset_id):
    self.inspector.inspect_object(ProjectPart.ASSETS, asset_id, self.proj_manager.asset_manager.get_as_dict(asset_id))

  @Slot(str)
  def scene_selected(self, scene_id):
    self.inspector.inspect_object(ProjectPart.SCENES, scene_id, self.proj_manager.scene_manager.get_as_dict(scene_id))

  @Slot(str)
  def entity_selected(self, entity_id):
    self.inspector.inspect_object(ProjectPart.ENTITIES, entity_id, self.proj_manager.entity_manager.get_as_dict(entity_id))

  @Slot(ProjectPart, str, str, str)
  def update_property(self, type: ProjectPart, name: str, property_name: str, new_value: str):
    pass
