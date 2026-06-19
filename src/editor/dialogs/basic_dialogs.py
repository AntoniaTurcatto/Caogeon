from configparser import NoOptionError
from random import seed
from typing import Callable

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from editor.validators import PathValidator

class BasicDialog(QDialog):
  on_confirm = Signal(str)
  on_cancel = Signal()

  def __init__(self, width: int, height: int, parent: QWidget | None = None, validator: QValidator | None = None):
    super().__init__(parent)
    self.setModal(True)
    self._validator = validator
    self.caption_lb = QLabel()
    self.edit = QLineEdit()

    self.cancel_btn = QPushButton("Cancel")
    self.confirm_btn = QPushButton("Confirm")
    self.cancel_btn.clicked.connect(self.on_cancel_slot)
    self.confirm_btn.clicked.connect(self.on_confirm_slot)

    edit_layout = QHBoxLayout()
    edit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    edit_layout.addWidget(self.caption_lb)
    edit_layout.addWidget(self.edit)

    btn_layout = QHBoxLayout()
    btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
    btn_layout.addWidget(self.cancel_btn)
    btn_layout.addWidget(self.confirm_btn)

    main_layout = QVBoxLayout()
    main_layout.addLayout(edit_layout)
    main_layout.addLayout(btn_layout)
    self.setFixedSize(width, height)
    self.setLayout(main_layout)

    if self._validator is not None:
      self.edit.setValidator(self._validator)

  def create_buttons(self):
    # TODO: Add custom buttons here for overriding
    pass

  @Slot()
  def on_confirm_slot(self):
    text = self.edit.text()
    if self.edit.validator() is not None:
      state = self.edit.validator().validate(text, 0)
      if state != QValidator.State.Acceptable:
        self.edit.setFocus()
        self.edit.selectAll()
        return

    if self.on_confirm is not None:
      self.on_confirm.emit(text)
    self.close()

  @Slot()
  def on_cancel_slot(self):
    if self.on_cancel is not None:
      self.on_cancel.emit()
    self.close()

  def disconnect_on_confirm(self):
    try:
      self.on_confirm.disconnect()
    except RuntimeError:
      pass

  def disconnect_on_cancel(self):
    try:
      self.on_cancel.disconnect()
    except RuntimeError:
      pass

  def show(self,
    caption: str,
    on_confirm: Callable[[str], None],
    on_cancel: Callable[[], None] | None = None):
    self.caption_lb.setText(caption)

    self.disconnect_on_confirm()
    self.disconnect_on_cancel()
    self.on_confirm.connect(on_confirm)
    if on_cancel is not None:
      self.on_cancel.connect(on_cancel)
    super().show()
    self.edit.setFocus()


class PathDialog(BasicDialog):
  def __init__(self, parent: QWidget | None = None):
    super().__init__(400, 100, parent=parent, validator=PathValidator())
    self.setWindowTitle("Select Path")

class ErrorDialog(BasicDialog):
  def __init__(self, parent: QWidget | None = None):
    super().__init__(400, 100, parent=parent)
    self.setWindowTitle("Error")
