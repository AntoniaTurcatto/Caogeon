import sys
from PySide6.QtCore import (Signal, Slot, Qt)
from PySide6.QtWidgets import (QApplication,
                               QLabel,
                               QLineEdit, QMainWindow, QMenuBar,
                               QPushButton,
                               QVBoxLayout, QHBoxLayout)

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Caogeon editor")
        self.init_ui()

    def init_ui(self):
        self.setMenuBar(Menu(self))

    @Slot()
    def new_project(self):
        print("new")

    @Slot()
    def open_project(self):
        print("open")

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

    def add_project_menu(self, main_window: MainWindow):
        project_menu = self.addMenu("file")
        project_menu.addAction("new project").triggered.connect(main_window.new_project)
        project_menu.addAction("open project").triggered.connect(main_window.open_project)
        project_menu.addAction("save project").triggered.connect(main_window.save_project)
        project_menu.addAction("save files").triggered.connect(main_window.save_files)
        project_menu.addAction("import asset").triggered.connect(main_window.import_asset)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
