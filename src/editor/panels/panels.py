from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QVBoxLayout, QLabel, QWidget


class BrowserPanel(QWidget):

  selected = Signal(str)

  def __init__(self, parent=None, title=""):
    super().__init__(parent)

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(QLabel(f"<b>{title}</b>"))

    self.list_widget = QListWidget()
    main_layout.addWidget(self.list_widget)

    self.list_widget.currentTextChanged.connect(self._on_item_changed)
    self.setLayout(main_layout)

  def load_assets(self, values: list[str]):
    self.list_widget.clear()
    self.list_widget.addItems(values)

  def _on_item_changed(self, current_text: str):
    if current_text:
        self.selected.emit(current_text)
