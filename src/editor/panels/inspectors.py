from abc import abstractmethod
from pathlib import Path
from re import A
from typing import Generic, TypeVar, Callable, get_args
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget

from core.model import Asset, Entity, ProjectPart, ProjectPartBase, Scene
from core.registers import Registry

TProjectPartBase = TypeVar("TProjectPartBase", bound=ProjectPartBase)

class ProjectPartSelector(QComboBox, Generic[TProjectPartBase]):
  asset_changed = Signal(object)

  def __init__(self, objs: Registry[TProjectPartBase], allow_none: bool = True, parent=None):
    super().__init__(parent)
    self.objs = objs
    self.objs.on_change.append(self.reload_and_restore)
    self.allow_none = allow_none
    self.reload()

  def reload(self):
    self.clear()
    if self.allow_none:
      self.addItem("", None)
    for obj in self.objs:
      self.addItem(obj.unique_name, obj)

  def reload_and_restore(self):
    current_item = self.currentData()
    self.reload()
    if current_item is not None:
      self.setCurrentText(current_item.unique_name)

  def selected(self) -> TProjectPartBase | None:
    return self.currentData()

class PathSelector(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    layout = QHBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    self.path_edit = QLineEdit()
    layout.addWidget(self.path_edit)
    self.browse_button = QPushButton("Browse")
    layout.addWidget(self.browse_button)
    self.browse_button.clicked.connect(self.browse)

  def browse(self):
    path = QFileDialog.getExistingDirectory(self, "Select Directory")
    if path:
      self.path_edit.setText(path)

class InspectorWidgetFactory:
  def __init__(self, assets: Registry[Asset], entities: Registry[Entity], scenes: Registry[Scene]) -> None:
    self.assets = assets
    self.entities = entities
    self.scenes = scenes
    self.widget_map: dict[type, Callable[[], QWidget]] = {
      str: lambda: QLineEdit(),
      int: lambda: QSpinBox(),
      Asset: lambda: ProjectPartSelector(self.assets),
      Entity: lambda: ProjectPartSelector(self.entities),
      Scene: lambda: ProjectPartSelector(self.scenes),
      Path: lambda: PathSelector(),
    }

  def create_widget(self, type_var: type) -> QWidget:
    type_var = self.resolve_optional(type_var)
    widget_factory = self.widget_map.get(type_var)
    if widget_factory:
      return widget_factory()
    return QLineEdit()

  def resolve_optional(self, type_var: type) -> type:
    args = get_args(type_var)
    if type(None) in args:
      non_none_args = [arg for arg in args if arg is not type(None)]
      if len(non_none_args) == 1:
        return non_none_args[0]
    return type_var

class GenericInspectorPanel(QWidget):

  # Project part, object id, property name, new value
  property_changed = Signal(ProjectPart,str, str, str)

  def __init__(self, parent = None):
    super().__init__(parent)
    self.project_part: ProjectPart | None = None
    self.id: str = ""

    self.main_layout = QVBoxLayout(self)
    self.main_layout.setContentsMargins(0, 0, 0, 0)

    self.title_label = QLabel("<b>Object Inspector</b>")
    self.main_layout.addWidget(self.title_label)

    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    self.main_layout.addWidget(self.scroll_area)

    self.form_widget = QWidget()
    self.form_layout = QFormLayout(self.form_widget)
    self.scroll_area.setWidget(self.form_widget)

  def inspect_object(self, proj_part: ProjectPart, obj_id: str, properties: dict):
    """Builds the form fields based on the provided dictionary."""
    self.clear()
    self.project_part = proj_part
    self.id = obj_id
    self.title_label.setText(f"<b>Inspector: {obj_id}</b>")

    for key, value in properties.items():
      line_edit = QLineEdit(str(value))
      line_edit.editingFinished.connect(
        lambda k=key, w=line_edit: self._on_value_edited(k, w.text())
      )

      self.form_layout.addRow(key, line_edit)

  def clear(self):
    """Removes all rows from the form."""
    while self.form_layout.rowCount() > 0:
      self.form_layout.removeRow(0)
    self.title_label.setText("<b>Object Inspector</b>")

  def _on_value_edited(self, key: str, new_value: str):
    self.property_changed.emit(self.project_part, self.id, key, new_value)
