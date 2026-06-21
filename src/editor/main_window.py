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
from editor.dialogs.basic_dialogs import DialogManager

class MainWindow(QMainWindow):
    def __init__(self, project_mgr: ProjectManager, dialogs_mgr: DialogManager, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Caogeon editor")
        self.init_ui()
        self.dialogs_mgr = dialogs_mgr
        #self.dialogs_mgr.set_parent(self)
        self.proj_mgr = project_mgr
        self.setMinimumSize(800, 600)

    def init_ui(self):
        self.setMenuBar(Menu(self))

    @Slot()
    def new_project(self):
        print("new")

    @Slot()
    def on_confirm_open_project(self):
      try:
        self.proj_mgr.load(ProjectPaths(Path(self.dialogs_mgr.path_dialog.get_input())))
      except Exception as e:
        self.dialogs_mgr.error_dialog.show("Failed to open project: " + str(e))

    @Slot()
    def open_project(self):
        self.dialogs_mgr.path_dialog.show("Path", self.on_confirm_open_project)

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
