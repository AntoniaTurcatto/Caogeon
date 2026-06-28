from abc import abstractmethod
from ast import Slice
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar, get_args, get_origin

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QInputDialog, QLineEdit, QListWidget, QMessageBox, QPushButton, QSpinBox, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.managers import TProjectPartBase
from core.model import Asset, Entity, InstancedEntity, ProjectPartBase, PropertyChange, Scene
from core.registers import Registry
from core.scene_manager import SceneManager


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
    self.destroyed.connect(self._on_qt_destroyed)

  @Slot(QObject)
  def _on_qt_destroyed(self, _: QObject):
    self.on_pre_destroy()

  @abstractmethod
  def create_widget(self, parent=None) -> TGenericWidget: ...

  @abstractmethod
  def bind_signals_and_slots(self, widget: TGenericWidget): ...

  @abstractmethod
  def get_value(self) -> Any: ...

  def set_value(self, value, owner: Any | None = None):
    """For subclasses to override. Should set the value of the widget and owner to the given value (if not None)."""
    self._owner = owner

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

  def set_value(self, value: str, owner: Any | None = None):
    super().set_value(value, owner)
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

  def set_value(self, value: int, owner: Any | None = None):
    super().set_value(value, owner)
    self.widget.setValue(value)

  def create_widget(self, parent=None) -> QSpinBox:
    return QSpinBox(parent)

class PathWidget(BaseWidget[QWidget]):

  def __init__(self, parent=None):
    super().__init__(parent)

  def get_value(self) -> str:
    return self.path_edit.get_value()

  def set_value(self, value: str | Path, owner: Any | None = None):
    super().set_value(value, owner)
    if isinstance(value, Path):
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

  def set_value(self, obj: ProjectPartBase | None, owner: Any | None = None):
    super().set_value(obj, owner)
    self.on_pre_destroy()
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
      widget.set_value(getattr(self._obj, key), self._obj)
      widget.value_changed.connect(
          lambda val, k=key: self._on_change(k, val)
      )
      self.widget.setItemWidget(item, 1, widget)

  def on_pre_destroy(self):
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
    btn_row.setAlignment(Qt.AlignmentFlag.AlignRight)
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

  def set_value(self, value: list, owner: Any | None = None):
    super().set_value(value, owner)
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
    factory = self.factory.default_factory_map.get(self.item_type)
    if factory is None:
      return None
    return factory(self._owner)

  def on_pre_destroy(self):
    self._part_widget.on_pre_destroy()
    super().on_pre_destroy()

class DictWidget(BaseWidget[QWidget]):
  def __init__(self, key_type: type, value_type: type, factory: 'WidgetFactory', parent=None):
    from typing import Any as TypingAny
    self.key_type = key_type
    self._value_type_is_any = value_type is TypingAny
    self.value_type = value_type
    self.factory = factory
    self._data: dict = {}
    super().__init__(parent)

  def create_widget(self, parent=None) -> QWidget:
    container = QWidget(parent)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    self._tree = QTreeWidget()
    self._tree.setHeaderLabels(["Key", "Value"])
    self._tree.header().setStretchLastSection(True)
    self._tree.header().resizeSection(0, 120)
    layout.addWidget(self._tree)

    btn_row = QHBoxLayout()
    self._add_btn    = QPushButton("+")
    self._remove_btn = QPushButton("−")
    btn_row.addWidget(self._add_btn)
    btn_row.addWidget(self._remove_btn)
    btn_row.addStretch()
    layout.addLayout(btn_row)

    return container

  def bind_signals_and_slots(self, widget: QWidget):
    self._add_btn.clicked.connect(self._on_add)
    self._remove_btn.clicked.connect(self._on_remove)

  def _make_value_widget(self, value: Any) -> BaseWidget:
    if self._value_type_is_any:
      # infer by value type
      inferred = type(value) if value is not None else str
      return self.factory.create_widget(inferred) or StringWidget()
    return self.factory.create_widget(self.value_type) or StringWidget()

  def _pick_default_for_any(self) -> Any | None:
    """Asks the user for the type of the new value when value_type is Any."""
    type_options = ["str", "int", "float", "bool"]
    chosen, ok = QInputDialog.getItem(None, "Value type", "Type:", type_options, 0, False)
    if not ok:
      return None
    return {"str": str, "int": int, "float": float, "bool": bool}[chosen]()

  def _add_row(self, key: str, value: Any):
    item = QTreeWidgetItem(self._tree)
    item.setData(0, Qt.ItemDataRole.UserRole, key)

    key_widget = StringWidget()
    key_widget.set_value(key)
    key_widget.value_changed.connect(lambda new_key, i=item: self._on_key_changed(i, new_key))
    self._tree.setItemWidget(item, 0, key_widget)

    val_widget = self._make_value_widget(value)
    val_widget.set_value(value)
    val_widget.value_changed.connect(lambda val, i=item: self._on_value_changed(i, val))
    self._tree.setItemWidget(item, 1, val_widget)

  def _on_key_changed(self, item: QTreeWidgetItem, new_key: str):
    old_key = item.data(0, Qt.ItemDataRole.UserRole)
    if not new_key or new_key == old_key:
      return
    if new_key in self._data:
      QMessageBox.warning(None, "Duplicate key", f"'{new_key}' already exists")
      return
    value = self._data.pop(old_key)
    self._data[new_key] = value
    item.setData(0, Qt.ItemDataRole.UserRole, new_key)
    self.value_changed.emit(dict(self._data))

  def _on_value_changed(self, item: QTreeWidgetItem, value: Any):
    key = item.data(0, Qt.ItemDataRole.UserRole)
    if key in self._data:
      self._data[key] = value
      self.value_changed.emit(dict(self._data))

  def _on_add(self):
    key, ok = QInputDialog.getText(None, "New entry", "Key:")
    if not ok or not key:
      return
    if key in self._data:
      QMessageBox.warning(None, "Duplicate key", f"'{key}' already exists")
      return

    if self._value_type_is_any:
      default_val = self._pick_default_for_any()
      if default_val is None:
        return
    else:
      try:
        default_val = self.value_type()
      except TypeError:
        default_val = ""

    self._data[key] = default_val
    self._add_row(key, default_val)
    self.value_changed.emit(dict(self._data))

  def _on_remove(self):
    item = self._tree.currentItem()
    if item is None:
      return
    key = item.data(0, Qt.ItemDataRole.UserRole)
    self._data.pop(key, None)
    self._tree.takeTopLevelItem(self._tree.indexOfTopLevelItem(item))
    self.value_changed.emit(dict(self._data))

  def get_value(self) -> dict:
    return self._data

  def set_value(self, value: dict, owner: Any | None = None):
    super().set_value(value, owner)
    self._data = value if value is not None else {}
    self._reload()

  def _reload(self):
    self._tree.clear()
    for key, val in self._data.items():
      self._add_row(str(key), val)

  def on_pre_destroy(self):
    for i in range(self._tree.topLevelItemCount()):
      item = self._tree.topLevelItem(i)
      if item is None:
        continue
      for col in (0, 1):
        widget = self._tree.itemWidget(item, col)
        if isinstance(widget, BaseWidget):
          widget.on_pre_destroy()
    super().on_pre_destroy()

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

  def set_value(self, value: TProjectPartBase | None, owner: Any | None = None):
    super().set_value(value, owner)
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
  def __init__(self, asset_mgr: AssetManager, entity_mgr: EntityManager, scene_mgr: SceneManager) -> None:
    self.asset_mgr = asset_mgr
    self.entity_mgr = entity_mgr
    self.scene_mgr = scene_mgr
    self.list_item_type: type = str
    self.default_factory: Callable[[], Any] | None = None
    self.widget_map: dict[type, Callable[[], BaseWidget]] = {
      str: lambda: StringWidget(),
      int: lambda: IntWidget(),
      list: lambda: ListWidget(self.list_item_type, self, self.default_factory),
      dict: lambda: DictWidget(self.key_type, self.value_type, self),
      Asset: lambda: ProjectPartSelector(self.asset_mgr.assets),
      Entity: lambda: ProjectPartSelector(self.entity_mgr.entities),
      Scene: lambda: ProjectPartSelector(self.scene_mgr.scenes),
      InstancedEntity: lambda: ProjectPartWidget(self),
      Path: lambda: PathWidget(),
    }
    self.default_factory_map: dict[type, Callable[[Any], Any]] = {
      InstancedEntity: lambda owner: self._instanced_entity_factory(owner),
    }

  def create_widget(self, type_var: type) -> BaseWidget | None:
    type_var = self.resolve_optional(type_var)
    origin = get_origin(type_var)

    if origin is list:
      self.list_item_type = get_args(type_var)[0]
      type_var = origin
    elif origin is dict:
      self.key_type = get_args(type_var)[0]
      self.value_type = get_args(type_var)[1]
      type_var = origin

    widget_factory = self.widget_map.get(type_var)
    if widget_factory:
      widget = widget_factory()
      return widget
    return None

  def resolve_optional(self, type_var: type) -> type:
    origin = get_origin(type_var)
    if origin is None:
      return type_var
    args = get_args(type_var)
    if type(None) in args:
      non_none = [a for a in args if a is not type(None)]
      if len(non_none) == 1:
        return non_none[0]
    return type_var

  def _instanced_entity_factory(self, owner: Any) -> InstancedEntity | None:
    if not isinstance(owner, Scene):
      return None
    entities = self.entity_mgr.entities.as_list()
    if not entities:
      QMessageBox.warning(None, "0 entities found", "Create some before")
      return None
    names = [e.unique_name for e in entities]
    chosen, ok = QInputDialog.getItem(None, "Choose entity", "Entity:", names, 0, False)
    if not ok:
      return None
    entity = self.entity_mgr.entities.get(chosen)
    if not entity:
      QMessageBox.warning(None, "Entity not found", "The chosen entity does not exist")
      return None
    return self.scene_mgr.create_instanced_entity(owner, entity)
