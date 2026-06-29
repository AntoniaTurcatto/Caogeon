from imaplib import ParseFlags
import sys

from PySide6.QtWidgets import QApplication

from core.project_manager import ProjectManager
from editor.dialogs.manager import DialogManager
from editor.main_window import MainWindow

def init_editor(project_mgr: ProjectManager):
  app: QApplication = QApplication(sys.argv)
  dialogs_mgr = DialogManager(
    asset_manager=project_mgr.asset_manager,
    scene_manager=project_mgr.scene_manager,
    entity_manager=project_mgr.entity_manager
  )
  main_window: MainWindow = MainWindow(project_mgr, dialogs_mgr)
  main_window.showMaximized()
  sys.exit(app.exec())

def init_player(proj_mgr: ProjectManager):
  pass

def main():
  project_mgr = ProjectManager()
  if len(sys.argv) == 1:
    init_editor(project_mgr)
    return

  mode = sys.argv[1].lower()
  if mode == "p":
    init_player(project_mgr)
    return

  print(f"Unknown mode: {mode}")
  print("Usage:")
  print("  python main.py")
  print("  python main.py p")
  sys.exit(1)


if __name__ == "__main__":
    main()
