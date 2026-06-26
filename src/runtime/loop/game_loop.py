from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from core.model import InstancedEntity, Scene
from core.project_manager import ProjectManager

from runtime.api.runtime_api import RuntimeAPI
from runtime.io.input_state import InputState
from runtime.loader.loader import SceneLoader
from runtime.loop.render_data import RenderData, RenderEntity
from runtime.state import EntityRuntime, SceneRuntime

ON_SPAWN = "on_spawn"
ON_TICK = "on_tick"
ON_DESTROY = "on_destroy"


class BaseRuntime(ABC):
    # contrato que o GameRuntime implementa
    # o player só precisa conhecer essa interface

    @abstractmethod
    def tick(self, delta_time: float) -> None:
        pass

    @property
    @abstractmethod
    def render(self) -> Callable[[], RenderData]:
        pass

    @property
    @abstractmethod
    def api(self) -> RuntimeAPI:
        pass


class GameRuntime(BaseRuntime):
    # máquina de estados central do jogo
    # carrega cenas, roda o tick, aplica física e monta o pacote de render
    # tudo que o player precisa fazer é chamar tick() e consumir render()

    def __init__(self, project_manager: ProjectManager, project_path: str | Path) -> None:
        self.project_manager = project_manager
        self.project_path = Path(project_path)

        self._api = RuntimeAPI(self)
        self._loader = SceneLoader()

        self.input_state = InputState()
        self.game_state: dict[str, Any] = {}

        self.scene_runtime: SceneRuntime = SceneRuntime()
        self.current_scene_name: str = ""

        self.running: bool = True
        self.paused: bool = False

        self._instance_counter: int = 0
        self._destroy_queue: list[str] = []
        self._scene_change_queue: str | None = None

        initial_scene = self.project_manager.project.initial_scene  # type: ignore[union-attr]
        self._load_scene(initial_scene)

    @property
    def api(self) -> RuntimeAPI:
        return self._api

    # -- cenas --

    def _load_scene(self, scene: Scene) -> None:
        self._loader.clear_cache()
        self.scene_runtime = self._loader.build_scene_runtime(scene, self._api)
        self.current_scene_name = scene.unique_name
        self._run_scene_script(scene)
        self._emit_on_spawn_for_all()

    def _run_scene_script(self, scene: Scene) -> None:
        # executa on_load do script da cena, se tiver
        module = self._loader.load_scene_script(scene)
        if module is not None and hasattr(module, "on_load"):
            module.on_load(self._api, None)

    def _emit_on_spawn_for_all(self) -> None:
        for entity in list(self.scene_runtime.entities.values()):
            entity.send_message(ON_SPAWN, None)

    def queue_scene_change(self, scene_name: str) -> None:
        # a troca acontece só no fim do tick pra não quebrar o loop
        self._scene_change_queue = scene_name

    def _process_scene_change(self) -> None:
        if self._scene_change_queue is None:
            return

        scene_name = self._scene_change_queue
        self._scene_change_queue = None

        scene = self.project_manager.scene_manager.scenes.get(scene_name)
        if scene is None:
            raise ValueError(f"Cena '{scene_name}' não encontrada no projeto")

        self._load_scene(scene)

    # -- entidades --

    def spawn_entity(self, entity_name: str, x: float, y: float) -> str:
        # cria uma nova instância e retorna o id gerado
        entity = self.project_manager.entity_manager.entities.get(entity_name)
        if entity is None:
            raise ValueError(f"Entidade '{entity_name}' não encontrada no projeto")

        self._instance_counter += 1
        instance_id = f"{entity_name}_{self._instance_counter}"

        instanced = InstancedEntity(entity=entity, id=instance_id, x=int(x), y=int(y))
        entity_runtime = self._loader.build_entity_runtime(instanced, self._api)
        self.scene_runtime.register_entity(entity_runtime)

        entity_runtime.send_message(ON_SPAWN, None)
        return instance_id

    def queue_destroy(self, entity_id: str) -> None:
        # igual a troca de cena, a remoção acontece só no fim do tick
        if entity_id not in self._destroy_queue:
            self._destroy_queue.append(entity_id)

    def _process_destroys(self) -> None:
        for entity_id in self._destroy_queue:
            entity = self.scene_runtime.get_entity(entity_id)
            if entity is not None:
                entity.send_message(ON_DESTROY, None)
            self.scene_runtime.unregister_entity(entity_id)
        self._destroy_queue.clear()

    # -- tick --

    def tick(self, delta_time: float) -> None:
        # quando pausado, física e on_tick não rodam
        # mas destroy e troca de cena ainda são processados
        if not self.paused:
            self.scene_runtime.broadcast(ON_TICK, delta_time)

            for entity in self.scene_runtime.entities.values():
                entity.x += entity.velocity_x * delta_time
                entity.y += entity.velocity_y * delta_time

        self._process_destroys()
        self._process_scene_change()

    # -- render --

    @property
    def render(self) -> Callable[[], RenderData]:
        return self._build_render_data

    def _build_render_data(self) -> RenderData:
        # monta o pacote de render com as entidades visíveis ordenadas por z_index
        # background_path vazio significa sem background, o player renderiza preto
        scene = self.project_manager.scene_manager.scenes.get(self.current_scene_name)
        window = self.project_manager.project.window_specs  # type: ignore[union-attr]

        background_path = str(scene.background.path) if scene.background is not None else ""

        visible_entities = [
            RenderEntity(
                id=entity.id,
                entity_name=entity.entity_name,
                sprite_path=str(entity.instance.entity.sprite.path),
                x=entity.x,
                y=entity.y,
                width=entity.width,
                height=entity.height,
                z_index=entity.z_index,
                rotation=entity.rotation,
                scale_x=entity.scale_x,
                scale_y=entity.scale_y,
                flip_h=entity.flip_h,
                flip_v=entity.flip_v,
            )
            for entity in self.scene_runtime.entities.values()
            if entity.visible
        ]
        visible_entities.sort(key=lambda e: e.z_index)

        return RenderData(
            scene_name=scene.unique_name,
            background_path=background_path,
            window_title=window.title,
            window_width=window.width,
            window_height=window.height,
            entities=visible_entities,
            paused=self.paused,
        )
