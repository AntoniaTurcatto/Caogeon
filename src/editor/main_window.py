from pathlib import Path
import sys
from tkinter.constants import S
from PySide6.QtCore import (Signal, Slot, Qt)
from pathlib import Path

from PySide6.QtWidgets import (QApplication,
                               QLabel,
                               QLineEdit, QMainWindow, QMenu, QMenuBar,
                               QPushButton,
                               QVBoxLayout, QHBoxLayout)

from core.managers import ProjectPaths
from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import BasicDialog

class MainWindow(QMainWindow):
    def __init__(self, project_mgr: ProjectManager, dialogs: dict[str, BasicDialog], parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Caogeon editor")
        self.init_ui()
        self.dialog = dialogs["path"]
        self.error_dialog = dialogs["error"]
        self.proj_mgr = project_mgr
        self.setMinimumSize(800, 600)

    def init_ui(self):
        self.setMenuBar(Menu(self))

    @Slot()
    def new_project(self):
        print("new")

    @Slot(str)
    def on_confirm_open_project(self, path: str):
      try:
        self.proj_mgr.load(ProjectPaths(Path(path)))
      except Exception as e:
        print("Failed to open project: " + str(e))

    @Slot()
    def open_project(self):
        self.dialog.show("Path", self.on_confirm_open_project)

    @Slot()
    def save_files(self):
        pass

    @Slot()
    def save_project(self):
        pass

    @Slot()
    def import_asset(self):
        pass

class Menu(QMenuBar):
    def __init__(self, main_window: MainWindow) -> None:
        super().__init__()
        self.add_project_menu(main_window)

    def configure_project_menu(self, main_menu: QMenu):
        pass

    def add_project_menu(self, main_window: MainWindow):
        project_menu = self.addMenu("file")
        project_menu.addAction("new project").triggered.connect(main_window.new_project)
        project_menu.addAction("open project").triggered.connect(main_window.open_project)
        project_menu.addAction("save project").triggered.connect(main_window.save_project)
        project_menu.addAction("save files").triggered.connect(main_window.save_files)
        project_menu.addAction("import asset").triggered.connect(main_window.import_asset)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(ProjectManager())
    window.showMaximized()
    sys.exit(app.exec())
