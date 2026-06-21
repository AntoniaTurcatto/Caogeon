from imaplib import ParseFlags
import sys

from PySide6.QtWidgets import QApplication

from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import DialogManager
from editor.main_window import MainWindow

def init_editor(app: QApplication, project_mgr: ProjectManager, dialogs_mgr: DialogManager):

  main_window: MainWindow = MainWindow(project_mgr, dialogs_mgr)
  main_window.showMaximized()
  sys.exit(app.exec())

def main():
  app: QApplication = QApplication(sys.argv)
  dialogs_mgr = DialogManager()
  project_mgr = ProjectManager()
  init_editor(app, project_mgr, dialogs_mgr)

if __name__ == "__main__":
    main()
