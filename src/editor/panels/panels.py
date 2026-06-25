from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QListWidget, QMenu, QVBoxLayout, QLabel, QWidget


class BrowserPanel(QWidget):

  selected = Signal(str)
  removed = Signal(str)

  def __init__(self, parent=None, title=""):
    super().__init__(parent)

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(QLabel(f"<b>{title}</b>"))

    self.list_widget = QListWidget()
    main_layout.addWidget(self.list_widget)

    self.list_widget.currentTextChanged.connect(self._on_item_changed)
    self.setLayout(main_layout)

  def _configure_context_menu(self):
    self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.list_widget.customContextMenuRequested.connect(self._on_context_menu_requested)

  def update_item_label(self, old_label: str, new_label: str):
    print(f"updating item label: {old_label} -> {new_label}")
    item = self.list_widget.findItems(old_label, Qt.MatchFlag.MatchExactly)
    if item:
        item[0].setText(new_label)

  @Slot(int)
  def _on_context_menu_requested(self, pos):
    print("context menu requested")
    menu = QMenu(self)
    menu.addAction("Remove", self.remove_item)
    menu.exec_(self.list_widget.mapToGlobal(pos))

  def load_assets(self, values: list[str]):
    self.list_widget.clear()
    self.list_widget.addItems(values)

  def remove_item(self, row: int):
    item = self.list_widget.item(row)
    if item:
        self.removed.emit(item.text())

  def _on_item_changed(self, current_text: str):
    if current_text:
        self.selected.emit(current_text)
