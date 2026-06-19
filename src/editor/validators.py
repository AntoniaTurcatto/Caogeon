from pathlib import Path

from PySide6.QtGui import QValidator


class PathValidator(QValidator):
  def __init__(self, parent=None):
    super().__init__(parent)

  def validate(self, input_str: str, pos: int) -> QValidator.State:
    if Path(input_str).exists():
      return QValidator.State.Acceptable
    return QValidator.State.Intermediate
