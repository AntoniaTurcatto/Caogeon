from pathlib import Path
import shutil

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

  @staticmethod
  def copy_folder(origin: Path, dest: Path):
    if dest.exists():
      shutil.rmtree(dest)
    shutil.copytree(origin, dest)

  @staticmethod
  def copy_file(origin: Path, dest: Path) -> Path:
    """Copy a file from origin to dest. If dest already exists, create a new unique file name"""
    if not origin.exists():
      raise ValueError("Invalid origin")

    stem, suffix = dest.stem, dest.suffix
    counter = 0
    while dest.exists():
      dest = dest.with_name(f"{stem}_{counter}{suffix}")
      counter += 1
    shutil.copyfile(origin, dest)
    return dest

  @staticmethod
  def remove_files_from_dir(dir: Path):
    for entry in dir.iterdir():
      if entry.is_file():
        entry.unlink()
