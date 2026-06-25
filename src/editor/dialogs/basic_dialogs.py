from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, Signal, SignalInstance, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from editor.validators import PathValidator

class BasicDialog(QDialog):
  """
  Schema for all dialogs: legend, layout of buttons (aligned to the right),
  result via on_confirm and show() logic.
  """
  on_confirm = Signal()

  def __init__(self, width: int, height: int, parent: QWidget | None = None):
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
    main_layout.addLayout(self.btn_layout)
    self.setFixedSize(width, height)
    self.setLayout(main_layout)
    self._init_buttons()

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
    if self.on_confirm is not None:
      self.on_confirm.emit()
    self.close()

  def disconnect_slot(self, signal: SignalInstance):
    try:
      signal.disconnect()
    except RuntimeError:
      pass

  def show(self, caption: str, on_confirm: Callable[[], None] | None = None):
    self.caption_lb.setText(caption)
    self.disconnect_slot(self.on_confirm)
    if on_confirm is not None:
      self.on_confirm.connect(on_confirm)
    super().show()

class InputDialog(BasicDialog):
  """Dialog for inputting text."""

  on_cancel = Signal()

  def __init__(self, width: int = 400, height: int = 100, parent: QWidget | None = None, validator: QValidator | None = None):
    super().__init__(width, height, parent=parent)
    self.edit = QLineEdit()
    self.edit_layout.addWidget(self.edit)
    if validator is not None:
      self.edit.setValidator(validator)

  def _extra_buttons(self) -> list[tuple[str, Callable[[], None]]]:
    return [("Cancel", self.on_cancel_slot)]

  def get_input(self) -> str:
    return self.edit.text()

  @Slot()
  def on_cancel_slot(self):
    self.on_cancel.emit()
    self.close()

  @Slot()
  def on_confirm_slot(self):
    validator = self.edit.validator()
    if validator is not None:
      state = validator.validate(self.edit.text(), 0)
      if state != QValidator.State.Acceptable:
        self.edit.setFocus()
        self.edit.selectAll()
        return
    self.on_confirm.emit()
    self.close()

  def show(self, caption: str, on_confirm: Callable[[], None] | None = None, on_cancel: Callable[[], None] | None = None):
    self.disconnect_slot(self.on_cancel)
    if on_cancel is not None:
      self.on_cancel.connect(on_cancel)
    super().show(caption, on_confirm)
    self.edit.setFocus()

class PathDialog(InputDialog):
  def __init__(self, parent: QWidget | None = None):
    super().__init__(400, 100, parent=parent, validator=PathValidator())
    self.setWindowTitle("Select Path")
    self.setVisible(False)

  def get_input(self) -> Path:
    return Path(self.edit.text())

class ErrorDialog(BasicDialog):
  def __init__(self, parent: QWidget | None = None):
    super().__init__(400, 100, parent=parent)
    self.setVisible(False)
    self.setWindowTitle("Error")

class DialogManager:
  def __init__(self):
    self.path_dialog = PathDialog()
    self.error_dialog = ErrorDialog()
    self.input_dialog = InputDialog()
