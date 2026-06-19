from imaplib import ParseFlags
import sys

from PySide6.QtWidgets import QApplication

from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import BasicDialog, ErrorDialog, PathDialog
from editor.main_window import MainWindow

def init_editor(app: QApplication, project_mgr: ProjectManager, dialogs: dict[str, BasicDialog]):

  main_window: MainWindow = MainWindow(project_mgr, dialogs)
  main_window.showMaximized()
  sys.exit(app.exec())

def init_dialogs():
  return {"path": PathDialog(), "error": ErrorDialog()}

def main():
  app: QApplication = QApplication(sys.argv)
  dialogs = init_dialogs()
  project_mgr = ProjectManager()
  init_editor(app, project_mgr, dialogs)

if __name__ == "__main__":
    main()
