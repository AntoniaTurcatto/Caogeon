from pathlib import Path
from PySide6.QtCore import (Signal, Slot, Qt)
from pathlib import Path

from PySide6.QtWidgets import (QApplication,
                               QLabel,
                               QLineEdit, QMainWindow, QMenu, QMenuBar,
                               QPushButton, QSplitter,
                               QVBoxLayout, QHBoxLayout, QWidget)

from core.managers import ProjectPaths
from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import DialogManager
from editor.managers import EditorManager
from editor.panels.panels import BrowserPanel
from editor.panels.inspectors import GenericInspectorPanel

class MainWindow(QMainWindow):
    def __init__(self, project_mgr: ProjectManager, dialogs_mgr: DialogManager, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Caogeon editor")
        self.dialogs_mgr = dialogs_mgr
        self.proj_mgr = project_mgr
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.editor_mgr = EditorManager(self.proj_mgr, self.inspector_panel, self.asset_panel, self.scene_panel, self.entity_panel)

    def init_ui(self):
        self.setMenuBar(Menu(self))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        splitter_panels = QSplitter()
        splitter_panels.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(splitter_panels)
        self.init_proj_parts_panels(splitter_panels)

        self.canvas = QLabel("Scene Canvas Aqui")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setStyleSheet("background-color: #2b2b2b; color: white;")
        splitter.addWidget(self.canvas)

        self.inspector_panel = GenericInspectorPanel()
        splitter.addWidget(self.inspector_panel)

    def init_proj_parts_panels(self, splitter: QSplitter):
        self.scene_panel = BrowserPanel(title="Scene")
        self.entity_panel = BrowserPanel(title="Entities")
        self.asset_panel = BrowserPanel(title="Assets")
        splitter.addWidget(self.asset_panel)
        splitter.addWidget(self.scene_panel)
        splitter.addWidget(self.entity_panel)

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
