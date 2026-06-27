from typing import Callable

from core.entity_manager import EntityManager
from core.model import Asset, Entity
from core.registers import Registry
from editor.dialogs.basic_dialogs import ConfirmDialog
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from editor.widgets.base_widgets import ProjectPartSelector
from utils.files import PathUtils


class EntityCreationDialog(ConfirmDialog):
  def __init__(self, entity_manager: EntityManager, assets: Registry[Asset], width: int = 500, height: int = 300, parent=None):
    self._assets = assets
    self._entity_manager = entity_manager
    self.created_entity: Entity | None = None
    super().__init__(width, height, parent=parent)

  def _extra_layout_widgets(self) -> list[QWidget]:
    asset_select = QWidget()
    hbox = QHBoxLayout()
    caption = QLabel("Select an asset:")
    self.asset_selector = ProjectPartSelector(objs=self._assets)
    hbox.addWidget(caption)
    hbox.addWidget(self.asset_selector)
    asset_select.setLayout(hbox)
    return [
      asset_select
    ]

  def _clear(self):
    self.asset_selector.reload()

  def is_valid(self) -> bool:
    return self.asset_selector.get_value() is not None

  def before_confirm(self):
    asset = self.asset_selector.get_value()
    if asset is None:
      return
    self.created_entity = self._entity_manager.create(asset)
