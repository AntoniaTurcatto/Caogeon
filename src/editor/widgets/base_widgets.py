from abc import abstractmethod
from ast import Slice
from pathlib import Path
import re
from typing import Any, Callable, Generic, TypeVar, cast, get_args, get_origin

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QSpinBox, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from core.managers import TProjectPartBase
from core.model import Asset, Entity, InstancedEntity, ProjectPartBase, PropertyChange, Scene
from core.registers import Registry


TGenericWidget = TypeVar("TGenericWidget", bound=QWidget)

class BaseWidget(Generic[TGenericWidget], QWidget):
  value_changed = Signal(object)
  def __init__(self, parent=None) -> None:
    super().__init__(parent)
    self.widget = self.create_widget(self)
    layout = QHBoxLayout(self)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(self.widget)

    self.bind_signals_and_slots(self.widget)

  @abstractmethod
  def create_widget(self, parent=None) -> TGenericWidget: ...

  @abstractmethod
  def bind_signals_and_slots(self, widget: TGenericWidget): ...

  @abstractmethod
  def get_value(self) -> Any: ...

  @abstractmethod
  def set_value(self, value): ...

  def on_pre_destroy(self):
    """To subclasses to override if they have to do something before the widget is destroyed"""
    pass

class StringWidget(BaseWidget[QLineEdit]):
  def __init__(self, parent=None) :
    super().__init__(parent)

  def bind_signals_and_slots(self, widget: QLineEdit):
    widget.editingFinished.connect(self.editing_finished)

  def get_value(self) -> str:
    return self.widget.text()

  def set_value(self, value: str):
    self.widget.setText(value)

  def create_widget(self, parent=None) -> QLineEdit:
    return QLineEdit(parent)

  def get_line_edit(self) -> QLineEdit:
    return self.widget

  @Slot()
  def editing_finished(self):
    self.value_changed.emit(self.widget.text())

class IntWidget(BaseWidget[QSpinBox]):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.widget.setRange(-(2**31), 2**31 - 1)

  def bind_signals_and_slots(self, widget: QSpinBox):
    widget.valueChanged.connect(self.value_changed.emit)

  def get_value(self) -> int:
    return self.widget.value()

  def set_value(self, value: int):
    self.widget.setValue(value)

  def create_widget(self, parent=None) -> QSpinBox:
    return QSpinBox(parent)

class PathWidget(BaseWidget[QWidget]):

  def __init__(self, parent=None):
    super().__init__(parent)

  def get_value(self) -> str:
    return self.path_edit.get_value()

  def set_value(self, value):
    if not isinstance(value, str):
      value = str(value)
    self.path_edit.set_value(value)

  def bind_signals_and_slots(self, widget: QWidget):
    self.path_edit.value_changed.connect(self.value_changed.emit)
    self.browse_button.clicked.connect(self.browse)

  def browse(self):
    path = QFileDialog.getExistingDirectory(self, "Select Directory")
    if path:
      self.path_edit.set_value(path)

  def create_widget(self, parent):
    widget = QWidget(parent)

    layout = QHBoxLayout(widget)

    self.path_edit = StringWidget(widget)
    self.browse_button = QPushButton("Browse", widget)

    layout.addWidget(self.path_edit)
    layout.addWidget(self.browse_button)

    return widget

  def get_editor(self) -> StringWidget:
    return self.path_edit


class ProjectPartWidget(BaseWidget[QTreeWidget]):

  property_edited = Signal(PropertyChange)

  def __init__(self, factory: 'WidgetFactory', parent=None):
    super().__init__(parent)
    self._obj: ProjectPartBase | None = None
    self.factory = factory
    self.widget.setHeaderLabels(["Property", "Value"])
    self.widget.setAlternatingRowColors(True)
    self.widget.header().setStretchLastSection(True)
    self.widget.header().resizeSection(0, 130)

  def create_widget(self, parent=None) -> QTreeWidget:
    return QTreeWidget(parent)

  def set_value(self, obj: ProjectPartBase | None):
    self.pre_destroy_items()
    self.widget.clear()
    if obj is not None:
      self._obj = obj
    if self._obj is None:
      return

    for key, value in self._obj.property_types().items():
      item = QTreeWidgetItem(self.widget, [key])
      item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

      widget = self.factory.create_widget(value)
      if widget is None:
        continue
      widget.set_value(getattr(self._obj, key))
      widget.value_changed.connect(
          lambda val, k=key: self._on_change(k, val)
      )
      self.widget.setItemWidget(item, 1, widget)

  def pre_destroy_items(self):
    for i in range(self.widget.topLevelItemCount()):
      item = self.widget.topLevelItem(i)
      if item is None:
        continue
      widget = self.widget.itemWidget(item, 1)

      if isinstance(widget, BaseWidget):
          widget.on_pre_destroy()

  def bind_signals_and_slots(self, widget: QTreeWidget):
    self.property_edited.connect(self.value_changed.emit)

  def _on_change(self, prop: str, value: object) -> None:
    if self._obj is not None:
      self.property_edited.emit(
        PropertyChange(self._obj, prop, value)
      )

  def get_value(self) -> ProjectPartBase | None:
    return self._obj

class ListWidget(BaseWidget[QWidget]):
  def __init__(self, item_type: type, factory: 'WidgetFactory', parent=None) -> None:
    self.item_type = item_type
    self.factory = factory
    self.items = []
    super().__init__(parent)

  def create_widget(self, parent=None) -> QWidget:
    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    self._list = QListWidget()
    layout.addWidget(self._list)

    btn_row = QHBoxLayout()
    self._add_btn    = QPushButton("+")
    self._remove_btn = QPushButton("−")
    btn_row.addWidget(self._add_btn)
    btn_row.addWidget(self._remove_btn)
    btn_row.addStretch()
    layout.addLayout(btn_row)

    self._part_widget = ProjectPartWidget(self.factory)
    layout.addWidget(self._part_widget)

    return container

  def bind_signals_and_slots(self, widget: QWidget):
    self._list.currentRowChanged.connect(self._on_selection_changed)
    self._add_btn.clicked.connect(self._on_add)
    self._remove_btn.clicked.connect(self._on_remove)
    self._part_widget.property_edited.connect(self._on_prop_changed)

  def _on_selection_changed(self, row: int):
    if row < 0 or row >= len(self.items):
      self._part_widget.set_value(None)
      return
    self._part_widget.set_value(self.items[row])

  def _on_prop_changed(self, change: PropertyChange):
    row = self._list.currentRow()
    if row < 0 or row >= len(self.items):
      return
    setattr(self.items[row], change.property_name, change.new_value)
    self._list.item(row).setText(self.items[row].unique_name)
    self.value_changed.emit(list(self.items))

  def get_value(self) -> list:
    return self.items

  def set_value(self, value: list):
    self.items = value
    self._reload_list()

  def _reload_list(self):
    self._list.clear()
    for obj in self.items:
      self._list.addItem(obj.unique_name)

  def _on_remove(self):
    row = self._list.currentRow()
    if row < 0 or row >= len(self.items):
      return
    self.items.pop(row)
    self._reload_list()
    self._part_widget.set_value(None)
    self.value_changed.emit(list(self.items))

  def _on_add(self):
    new_item = self.create_default_item()
    if new_item is None:
      return
    self.items.append(new_item)
    self._reload_list()
    self._list.setCurrentRow(len(self.items) - 1)
    self.value_changed.emit(list(self.items))

  def create_default_item(self) -> Any | None:
      return None

class ProjectPartSelector(BaseWidget[QComboBox], Generic[TProjectPartBase]):

  def __init__(self, objs: Registry[TProjectPartBase], allow_none: bool = True, parent=None):
    super().__init__(parent)
    self.objs = objs
    self.objs.on_change.append(self.reload_and_restore)
    self.allow_none = allow_none
    self.reload()

  def reload(self):
    self.widget.clear()
    if self.allow_none:
      self.widget.addItem("", None)
    for obj in self.objs:
      self.widget.addItem(obj.unique_name, obj)

  def reload_and_restore(self):
    current_item = self.widget.currentData()
    self.reload()
    if current_item is not None:
      self.widget.setCurrentText(current_item.unique_name)

  def on_pre_destroy(self):
    print(f"Object destroyed: {self}")
    self.objs.on_change.remove(self.reload_and_restore)

  def get_value(self) -> TProjectPartBase | None:
    return self.widget.currentData()

  def set_value(self, value: TProjectPartBase | None):
    if value is None:
      self.widget.setCurrentIndex(0)
    else:
      self.widget.setCurrentText(value.unique_name)

  def bind_signals_and_slots(self, widget: QComboBox):
    widget.currentIndexChanged.connect(self.on_value_changed)

  @Slot(int)
  def on_value_changed(self, _: int):
    self.value_changed.emit(self.widget.currentData())

  def create_widget(self, parent=None) -> QComboBox:
    return QComboBox(parent)

class WidgetFactory:
  def __init__(self, assets: Registry[Asset], entities: Registry[Entity], scenes: Registry[Scene]) -> None:
    self.assets = assets
    self.entities = entities
    self.scenes = scenes
    self.list_item_type: type = str
    self.widget_map: dict[type, Callable[[], BaseWidget]] = {
      str: lambda: StringWidget(),
      int: lambda: IntWidget(),
      list: lambda: ListWidget(self.list_item_type, self),
      Asset: lambda: ProjectPartSelector(self.assets),
      Entity: lambda: ProjectPartSelector(self.entities),
      Scene: lambda: ProjectPartSelector(self.scenes),
      InstancedEntity: lambda: ProjectPartWidget(self),
      Path: lambda: PathWidget(),
    }

  def create_widget(self, type_var: type) -> BaseWidget | None:
    origin = get_origin(type_var)
    type_var = self.resolve_optional(type_var)
    if origin is list:
      self.list_item_type = type_var
      self.type_var = origin

    widget_factory = self.widget_map.get(type_var)
    if widget_factory:
      return widget_factory()
    return None

  def resolve_optional(self, type_var: type) -> type:
    args = get_args(type_var)
    if type(None) in args:
      non_none_args = [arg for arg in args if arg is not type(None)] # Any | None -> Any
      if len(non_none_args) == 1:
        return non_none_args[0]
    return type_var
