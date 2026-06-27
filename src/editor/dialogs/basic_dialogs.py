from pathlib import Path
from typing import Callable, Generic, cast

from PySide6.QtCore import Qt, Signal, SignalInstance, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from editor.validators import PathFolderValidator, PathValidator
from editor.widgets.base_widgets import BaseWidget, PathWidget, StringWidget, TGenericWidget

class BasicDialog(QDialog):
  """
  Schema for all dialogs: legend, layout of buttons (aligned to the right),
  result via on_confirm and show() logic.
  """
  on_confirm = Signal()

  def __init__(self, width: int = 400, height: int = 100, parent: QWidget | None = None):
    super().__init__(parent)
    self.setModal(True)
    self.caption_lb = QLabel()
    self.caption_lb.setWordWrap(True)

    self.edit_layout = QHBoxLayout()
    self.edit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.edit_layout.addWidget(self.caption_lb)

    self.btn_layout = QHBoxLayout()
    self.btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

    main_layout = QVBoxLayout()
    main_layout.addLayout(self.edit_layout)

    for widget in self._extra_layout_widgets():
      self.edit_layout.addWidget(widget)

    main_layout.addLayout(self.btn_layout)
    self.setFixedSize(width, height)
    self.setLayout(main_layout)
    self._init_buttons()

  def _extra_layout_widgets(self) -> list[QWidget]:
    """For subclasses to override. Will be added to the edit_layout before the buttons, vertically stacked."""
    return []

  def _clear(self):
    """For subclasses to override. Will be called before the dialog is shown."""
    pass

  def _init_buttons(self) -> None:
    extras = self._extra_buttons()
    for text, slot in extras:
      self.add_button(text, slot)
    self.add_button("Confirm", self.on_confirm_slot, default=True)

  def _extra_buttons(self) -> list[tuple[str, Callable[[], None]]]:
    """For subclasses to override."""
    return []

  def add_button(self, text: str, slot: Callable[[], None], default: bool = False) -> QPushButton:
    """Creates a button, connects the slot and adds it to the btn_layout.
    default=True makes this button respond to the Enter key
    (handles setAutoDefault/setDefault automatically).
    """
    btn = QPushButton(text)
    btn.clicked.connect(slot)
    btn.setAutoDefault(default)
    btn.setDefault(default)
    self.btn_layout.addWidget(btn)
    return btn

  @Slot()
  def on_confirm_slot(self) -> None:
    if not self.is_valid():
      return
    self.before_confirm()
    if self.on_confirm is not None:
      self.on_confirm.emit()
    self.close()

  def is_valid(self) -> bool:
    """For subclasses to override. If true, the dialog will be accepted when the user clicks the confirm button."""
    return True

  def before_confirm(self):
    """For subclasses to override. For extra operations before the dialog is confirmed and after is valid."""
    pass

  def disconnect_slot(self, signal: SignalInstance):
    try:
      signal.disconnect()
    except RuntimeError:
      pass

  def show(self, caption: str, on_confirm: Callable[[], None] | None = None):
    self._clear()
    self.caption_lb.setText(caption)
    self.disconnect_slot(self.on_confirm)
    if on_confirm is not None:
      self.on_confirm.connect(on_confirm)
    super().show()

class ConfirmDialog(BasicDialog):
  """Dialog for confirming an action."""

  on_cancel = Signal()

  def __init__(self, width: int = 400, height: int = 100, parent: QWidget | None = None):
    super().__init__(width, height, parent=parent)

  def _extra_buttons(self) -> list[tuple[str, Callable[[], None]]]:
    return [("Cancel", self.on_cancel_slot)]

  @Slot()
  def on_cancel_slot(self):
    self.on_cancel.emit()
    self.close()

class InputDialog(ConfirmDialog):
  """Dialog for inputting text."""

  def __init__(self, width: int = 400, height: int = 100, parent: QWidget | None = None, validator: QValidator | None = None):
    super().__init__(width, height, parent=parent)
    self.widget = self.create_widget()
    self.edit_layout.addWidget(self.widget)
    if validator is not None:
      self.get_editor().get_line_edit().setValidator(validator)

  def _clear(self):
    self.get_editor().get_line_edit().clear()

  def create_widget(self, parent: QWidget | None = None) -> QWidget:
    return StringWidget(parent)

  def get_widget(self) -> QWidget:
    return self.widget

  def get_editor(self) -> StringWidget:
    return cast(StringWidget, self.get_widget())

  def get_input(self) -> str:
    return self.get_editor().get_line_edit().text()

  @Slot()
  def on_confirm_slot(self):
    validator = self.get_editor().get_line_edit().validator()
    if validator is not None:
      state = validator.validate(self.get_editor().get_line_edit().text(), 0)
      if state != QValidator.State.Acceptable:
        self.get_editor().get_line_edit().setFocus()
        self.get_editor().get_line_edit().selectAll()
        return
    self.on_confirm.emit()
    self.close()

  def show(self, caption: str, on_confirm: Callable[[], None] | None = None, on_cancel: Callable[[], None] | None = None):
    self.disconnect_slot(self.on_cancel)
    if on_cancel is not None:
      self.on_cancel.connect(on_cancel)
    super().show(caption, on_confirm)
    self.get_editor().get_line_edit().setFocus()

class PathDialog(InputDialog):
  def __init__(self, parent: QWidget | None = None, validator: QValidator | None = None):
    super().__init__(400, 100, parent=parent, validator=validator)
    self.setWindowTitle("Select Path")
    self.setVisible(False)

  def create_widget(self, parent: QWidget | None = None) -> QWidget:
    return PathWidget(parent)

  def get_editor(self) -> StringWidget:
    return cast(PathWidget, self.get_widget()).get_editor()

  def get_input(self) -> Path:
    return Path(self.get_editor().get_line_edit().text())

class ErrorDialog(BasicDialog):
  def __init__(self, parent: QWidget | None = None):
    super().__init__(400, 100, parent=parent)
    self.setVisible(False)
    self.setWindowTitle("Error")

class DialogManager:
  def __init__(self):
    self.path_file_dialog = PathDialog(validator=PathValidator())
    self.path_folder_dialog = PathDialog(validator=PathFolderValidator())
    self.error_dialog = ErrorDialog()
    self.input_dialog = InputDialog()
    self.confirm_dialog = ConfirmDialog()
