from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from core.model import Asset, Entity, ProjectPartBase, PropertyChange, Scene
from core.project_manager import ProjectManager
from core.registers import Registry
from editor.widgets.base_widgets import ProjectPartWidget, WidgetFactory

class GenericInspectorPanel(QWidget):

  property_edited = Signal(PropertyChange)

  def __init__(self, proj_mgr: ProjectManager, parent: QWidget | None = None):
    super().__init__(parent)
    self._obj: ProjectPartBase | None = None
    self.factory = WidgetFactory(asset_mgr=proj_mgr.asset_manager, entity_mgr=proj_mgr.entity_manager, scene_mgr=proj_mgr.scene_manager)

    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(0, 0, 0, 0)

    self.title_label = QLabel("")
    main_layout.addWidget(self.title_label)

    self.obj_widget = ProjectPartWidget(self.factory)
    self.obj_widget.property_edited.connect(self.property_edited.emit)

    main_layout.addWidget(self.obj_widget)
    self.setLayout(main_layout)

  def inspect(self, obj: ProjectPartBase):
    """Builds the form fields based on obj's and inner types dictionary."""
    self.title_label.setText(f"<b>{obj.unique_name}</b>")
    self.obj_widget.set_value(obj)

  def clear(self):
    self.obj_widget.set_value(None)
    self.title_label.setText("")
    self._obj = None
