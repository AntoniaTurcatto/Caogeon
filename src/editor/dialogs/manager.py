from core.asset_manager import AssetManager
from core.entity_manager import EntityManager
from core.scene_manager import SceneManager
from editor.dialogs.basic_dialogs import ConfirmDialog, ErrorDialog, InputDialog, PathDialog
from editor.dialogs.model_dialogs import EntityCreationDialog
from editor.validators import PathFolderValidator, PathValidator
from editor.widgets.base_widgets import SearchMode


class DialogManager:
  def __init__(self, entity_manager: EntityManager, asset_manager: AssetManager, scene_manager: SceneManager):
    self.path_file_dialog = PathDialog(search_mode=SearchMode.FILE)
    self.path_folder_dialog = PathDialog(search_mode=SearchMode.FOLDER)
    self.error_dialog = ErrorDialog()
    self.input_dialog = InputDialog()
    self.confirm_dialog = ConfirmDialog()
    self.entity_creation_dialog = EntityCreationDialog(entity_manager=entity_manager, assets=asset_manager.assets)
