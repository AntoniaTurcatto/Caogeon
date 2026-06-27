from pathlib import Path

from core.managers import ProjectPaths

class PathUtils:
  @staticmethod
  def risk_of_overwrite(path: Path) -> bool:
    if not path.exists():
      return False
    return path.is_file() or (path.is_dir() and any(path.iterdir()))

  @staticmethod
  def create_empty_script(path_folder: Path, unique_name: str) -> Path:
    script_path = path_folder / f"{unique_name}.py"
    script_path.touch()
    return script_path
