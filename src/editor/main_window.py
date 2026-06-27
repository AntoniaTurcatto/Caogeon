from pathlib import Path
from typing import Callable
from PySide6.QtCore import (Slot, Qt)
from pathlib import Path

from PySide6.QtWidgets import (QLabel,
                               QMainWindow, QMenu, QMenuBar,
                               QSplitter,
                               QVBoxLayout, QWidget)

from core.managers import ProjectPaths
from core.project_manager import ProjectManager
from editor.dialogs.basic_dialogs import DialogManager
from editor.managers import EditorManager
from editor.panels.panels import BrowserPanel
from editor.panels.inspectors import GenericInspectorPanel
from utils.files import PathUtils

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
        self.setMenuBar(Menu(self.proj_mgr, self.dialogs_mgr))
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

        self.inspector_panel = GenericInspectorPanel(self.proj_mgr.asset_manager.assets, self.proj_mgr.entity_manager.entities, self.proj_mgr.scene_manager.scenes)
        splitter.addWidget(self.inspector_panel)

    def init_proj_parts_panels(self, splitter: QSplitter):
        self.scene_panel = BrowserPanel(title="Scene")
        self.entity_panel = BrowserPanel(title="Entities")
        self.asset_panel = BrowserPanel(title="Assets")
        splitter.addWidget(self.asset_panel)
        splitter.addWidget(self.scene_panel)
        splitter.addWidget(self.entity_panel)

class Menu(QMenuBar):
    def __init__(self, proj_mgr: ProjectManager, dialogs_mgr: DialogManager) -> None:
        super().__init__()
        self.proj_mgr = proj_mgr
        self.dialogs_mgr = dialogs_mgr
        self.add_project_menu()
        self.new_proj_path: Path | None = None

    def add_project_menu(self):
        project_menu = self.addMenu("file")
        project_menu.addAction("new project").triggered.connect(self.new_project)
        project_menu.addAction("load project").triggered.connect(self.load_project)
        project_menu.addAction("save project").triggered.connect(self.save_project)
        project_menu.addAction("save project at").triggered.connect(self.save_project_at)
        project_menu.addAction("import asset").triggered.connect(self.import_asset)

    @Slot()
    def new_project(self):
      self.dialogs_mgr.path_folder_dialog.show("Path", self.on_confirm_new_project)

    @Slot()
    def on_confirm_new_project(self):
      self.new_proj_path = self.dialogs_mgr.path_folder_dialog.get_input()
      self.confirm_override_if_aplicable(self.new_proj_path, self.new_project_name)

    def confirm_override_if_aplicable(self, path: Path, on_confirm: Callable[[], None]):
      if not PathUtils.risk_of_overwrite(path):
        on_confirm()
        return

      self.dialogs_mgr.confirm_dialog.show(f"Path {path} already exists. Override?", on_confirm)

    def new_project_name(self):
      self.dialogs_mgr.input_dialog.show("Name", self.on_confirm_new_project_name)

    @Slot()
    def on_confirm_new_project_name(self):
      if self.new_proj_path is None:
        self.dialogs_mgr.error_dialog.show("Please select a project path first.")
        return
      try:
        self.proj_mgr.new(ProjectPaths(self.new_proj_path), self.dialogs_mgr.input_dialog.get_input())
      except Exception as e:
        self.dialogs_mgr.error_dialog.show("Failed to create project: " + str(e))

    @Slot()
    def load_project(self):
      self.dialogs_mgr.path_folder_dialog.show("Path", self.on_confirm_load_project)

    @Slot()
    def on_confirm_load_project(self):
      try:
        self.proj_mgr.load(ProjectPaths(self.dialogs_mgr.path_folder_dialog.get_input()))
      except Exception as e:
        self.dialogs_mgr.error_dialog.show("Failed to open project: " + str(e))

    @Slot()
    def save_project_at(self):
      self.dialogs_mgr.path_folder_dialog.show("Path", self.on_confirm_save_project_at)

    @Slot()
    def on_confirm_save_project_at(self):
      save_as = self.dialogs_mgr.path_folder_dialog.get_input()
      try:
        self.proj_mgr.save(ProjectPaths(save_as))
      except Exception as e:
        self.dialogs_mgr.error_dialog.show(f"Failed to save project as {save_as}: {str(e)}")

    @Slot()
    def save_project(self):
      try:
        self.proj_mgr.save()
      except Exception as e:
        self.dialogs_mgr.error_dialog.show("Failed to save project: " + str(e))

    @Slot()
    def import_asset(self):
      self.dialogs_mgr.path_file_dialog.show("Path", self.on_confirm_import_asset)

    @Slot()
    def on_confirm_import_asset(self):
      try:
        self.proj_mgr.import_asset(self.dialogs_mgr.path_file_dialog.get_input())
      except Exception as e:
        self.dialogs_mgr.error_dialog.show("Failed to import asset: " + str(e))
