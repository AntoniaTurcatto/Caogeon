from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QListWidget, QMenu, QVBoxLayout, QLabel, QWidget

class BrowserListWidget(QListWidget):
  def focusOutEvent(self, event):
      self.clearSelection()
      self.setCurrentRow(-1)
      super().focusOutEvent(event)

class BrowserPanel(QWidget):

  # passes label of its selected item
  selected = Signal(str)
  create_opc_clicked = Signal()
  remove_opc_clicked = Signal(str)

  def __init__(self, parent=None, title="", can_add=True):
    super().__init__(parent)
    self.can_add = can_add

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(QLabel(f"<b>{title}</b>"))

    self.list_widget = BrowserListWidget()
    main_layout.addWidget(self.list_widget)

    self.list_widget.currentTextChanged.connect(self._on_item_changed)
    self.setLayout(main_layout)
    self._configure_context_menu()

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
    menu = QMenu(self)
    item = self.list_widget.itemAt(pos)
    if self.can_add:
      menu.addAction("Create", self.create_opc_clicked.emit)
    if item:
      menu.addAction("Remove", lambda: self.remove_opc_clicked.emit(item.text()))
    menu.exec_(self.list_widget.mapToGlobal(pos))

  def load_assets(self, values: list[str]):
    self.list_widget.clear()
    self.list_widget.addItems(values)

  @Slot(str)
  def _on_item_changed(self, text: str):
    if text != "":
      self.selected.emit(text)
