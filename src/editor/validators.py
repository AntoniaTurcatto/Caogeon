from pathlib import Path

from PySide6.QtGui import QValidator


class PathValidator(QValidator):
  def __init__(self, parent=None):
    super().__init__(parent)

  def validate(self, input_str: str, pos: int) -> QValidator.State:
    path = Path(input_str)
    if self.is_valid(path):
      return QValidator.State.Acceptable
    return QValidator.State.Intermediate

  def is_valid(self, path: Path) -> bool:
    return path.exists()

class PathFileValidator(PathValidator):
  def __init__(self, parent=None):
    super().__init__(parent)

  def validate(self, input_str: str, pos: int) -> QValidator.State:
    path = Path(input_str)
    if self.is_valid(path):
      return QValidator.State.Acceptable
    return QValidator.State.Intermediate

  def is_valid(self, path: Path) -> bool:
    return super().is_valid(path) and path.is_file()

class PathFolderValidator(PathValidator):
  def __init__(self, parent=None):
    super().__init__(parent)

  def validate(self, input_str: str, pos: int) -> QValidator.State:
    path = Path(input_str)
    if self.is_valid(path):
      return QValidator.State.Acceptable
    return QValidator.State.Intermediate

  def is_valid(self, path: Path) -> bool:
    return super().is_valid(path) and path.is_dir()
