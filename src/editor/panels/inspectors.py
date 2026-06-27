from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from core.model import Asset, Entity, ProjectPartBase, PropertyChange, Scene
from core.registers import Registry
from editor.widgets.base_widgets import ProjectPartWidget, WidgetFactory

class GenericInspectorPanel(QWidget):

  property_edited = Signal(PropertyChange)

  def __init__(self, assets: Registry[Asset], entities: Registry[Entity], scenes: Registry[Scene], parent: QWidget | None = None):
    super().__init__(parent)
    self._obj: ProjectPartBase | None = None
    self.factory = WidgetFactory(assets=assets, entities=entities, scenes=scenes)

    self.main_layout = QVBoxLayout(self)
    self.main_layout.setContentsMargins(0, 0, 0, 0)

    self.title_label = QLabel("")
    self.main_layout.addWidget(self.title_label)

    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True)
    self.main_layout.addWidget(self.scroll_area)

    self.form_widget = QWidget()
    self.obj_widget = ProjectPartWidget(self.factory, self.form_widget)
    self.obj_widget.property_edited.connect(self.property_edited.emit)

    self.scroll_area.setWidget(self.form_widget)

  def inspect(self, obj: ProjectPartBase):
    """Builds the form fields based on obj's and inner types dictionary."""
    self.obj_widget.reload(obj)

  def clear(self):
    self.obj_widget.widget.clear()
    self.title_label.setText("")
    self._obj = None

  def _on_change(self, prop: str, value: object) -> None:
    if self._obj is not None:
      self.property_edited.emit(
        PropertyChange(self._obj, prop, value)
      )
