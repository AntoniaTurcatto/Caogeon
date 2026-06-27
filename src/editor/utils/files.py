from pathlib import Path

class PathUtils:
  @staticmethod
  def risk_of_overwrite(path: Path) -> bool:
    if not path.exists():
      return False
    return path.is_file() or (path.is_dir() and any(path.iterdir()))
