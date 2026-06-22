from pathlib import Path
from PySide6.QtCore import (Signal, Slot, Qt)
from pathlib import Path

from PySide6.QtWidgets import (QApplication,
                               QLabel,
                               QLineEdit, QMainWindow, QMenu, QMenuBar,
                               QPushButton, QSplitter,
                               QVBoxLayout, QHBoxLayout, QWidget)

from core.managers import ProjectPaths
from core.model import ProjectPart
from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import DialogManager
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

    def init_ui(self):
        self.setMenuBar(Menu(self))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        self.asset_panel = BrowserPanel(title="Assets")
        self.asset_panel.load_assets([asset.unique_name for asset in self.proj_mgr.asset_manager.assets.as_list()])
        splitter.addWidget(self.asset_panel)

        self.canvas = QLabel("Scene Canvas Aqui")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setStyleSheet("background-color: #2b2b2b; color: white;")
        splitter.addWidget(self.canvas)

        self.inspector_panel = GenericInspectorPanel()
        splitter.addWidget(self.inspector_panel)

        self.asset_panel.selected.connect(self.on_asset_selected)
        self.inspector_panel.property_changed.connect(self.on_property_changed)

    @Slot(str)
    def on_asset_selected(self, asset_name: str):
        asset_dict = self.proj_mgr.asset_manager.get_as_dict(asset_name)
        if asset_dict:
            self.inspector_panel.inspect_object(ProjectPart.ASSET, asset_name, asset_dict)

    @Slot(ProjectPart, str, str, str)
    def on_property_changed(self, proj_part: ProjectPart, unique_name: str, property_name: str, new_value: str):
        self.proj_mgr.update_property(proj_part, unique_name, property_name, new_value)

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
