from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QScrollArea, QVBoxLayout, QWidget
from core.model import ProjectPart


class GenericInspectorPanel(QWidget):

  # project_part, obj_id, key, new_value
  property_changed = Signal(ProjectPart, str, str, str)

  def __init__(self, parent = None):
    super().__init__(parent)
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

    self.current_obj_id = None
    self.project_part = None

  def inspect_object(self, project_part: ProjectPart, obj_id: str, properties: dict):
    """Builds the form fields based on the provided dictionary."""
    self.clear()
    self.current_obj_id = obj_id
    self.project_part = project_part
    self.title_label.setText(f"<b>Inspector: {obj_id}</b>")

    for key, value in properties.items():
      line_edit = QLineEdit(str(value))

      # The lambda needs to capture the iterated variables (k=key, w=line_edit)
      # editingFinished is triggered when the user presses Enter or moves the focus away from the field
      line_edit.editingFinished.connect(
        lambda k=key, w=line_edit: self._on_value_edited(k, w.text())
      )

      self.form_layout.addRow(key, line_edit)

  def clear(self):
    """Removes all rows from the form."""
    while self.form_layout.rowCount() > 0:
      self.form_layout.removeRow(0)
    self.current_obj_id = None
    self.title_label.setText("<b>Object Inspector</b>")

  def _on_value_edited(self, key: str, new_value: str):
    self.property_changed.emit(self.project_part, self.current_obj_id, key, new_value)
