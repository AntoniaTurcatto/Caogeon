from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from runtime.loop.game_loop import GameRuntime


class RuntimeAPI:
    # interface que os scripts do usuário usam pra interagir com o runtime
    # passada como ctx pra todos os hooks de entidade e scripts de cena
    # os scripts nunca acessam o GameRuntime diretamente

    def __init__(self, game_runtime: "GameRuntime") -> None:
        self._runtime = game_runtime

    # -- entidades --

    def spawn_entity(self, entity_name: str, x: float, y: float) -> str:
        # cria uma instância e retorna o id
        return self._runtime.spawn_entity(entity_name, x, y)

    def destroy_entity(self, entity_id: str) -> None:
        # marca pra remover no fim do tick
        self._runtime.queue_destroy(entity_id)

    def get_entity_properties(self, entity_id: str) -> dict | None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is None:
            return None
        return {
            "id": entity.id,
            "entity_name": entity.entity_name,
            "x": entity.x,
            "y": entity.y,
            "width": entity.width,
            "height": entity.height,
            "visible": entity.visible,
            "z_index": entity.z_index,
            "rotation": entity.rotation,
            "scale_x": entity.scale_x,
            "scale_y": entity.scale_y,
            "state": entity.state,
        }

    def get_entities_by_name(self, entity_name: str) -> list[str]:
        # retorna os ids de todas as partes ativas desse estilo
        return [
            e.id
            for e in self._runtime.scene_runtime.entities.values()
            if e.entity_name == entity_name
        ]

    def get_entities_in_area(self, x: float, y: float, w: float, h: float) -> list[str]:
        # retorna ids das entidades do hitbox intersecta a parte dada
        result = []
        for e in self._runtime.scene_runtime.entities.values():
            if e.x < x + w and e.x + e.width > x and e.y < y + h and e.y + e.height > y:
                result.append(e.id)
        return result

    def set_entity_visible(self, entity_id: str, visible: bool) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.visible = visible

    def set_entity_z_index(self, entity_id: str, z: int) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.z_index = z

    def get_entity_count(self) -> int:
        return len(self._runtime.scene_runtime.entities)

    # movimentacao

    def set_position(self, entity_id: str, x: float, y: float) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.x = x
            entity.y = y

    def move_entity(self, entity_id: str, dx: float, dy: float) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.x = entity.x + dx
            entity.y = entity.y + dy

    def get_position(self, entity_id: str) -> tuple[float, float] | None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is None:
            return None
        return entity.x, entity.y

    def set_rotation(self, entity_id: str, angle_degrees: float) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.rotation = angle_degrees

    def set_scale(self, entity_id: str, scale_x: float, scale_y: float) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.scale_x = scale_x
            entity.scale_y = scale_y

    def flip_entity(self, entity_id: str, horizontal: bool, vertical: bool) -> None:
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.flip_h = horizontal
            entity.flip_v = vertical

    #fisicas

    def set_velocity(self, entity_id: str, vx: float, vy: float) -> None:
        # velocidade em pixels por segundo
        entity = self._runtime.scene_runtime.get_entity(entity_id)
        if entity is not None:
            entity.velocity_x = vx
            entity.velocity_y = vy

    #inputs

    def is_key_held(self, key_name: str) -> bool:
        # True enquanto a tecla estiver segurada
        return key_name in self._runtime.input_state.keys_down

    def is_key_pressed(self, key_name: str) -> bool:
        # True só no frame em que a tecla foi pressionada
        return key_name in self._runtime.input_state.keys_pressed

    def is_key_released(self, key_name: str) -> bool:
        # True só no frame em que a tecla foi solta
        return key_name in self._runtime.input_state.keys_released

    def get_mouse_position(self) -> tuple[float, float]:
        return self._runtime.input_state.mouse_x, self._runtime.input_state.mouse_y

    def is_mouse_held(self, button: int = 0) -> bool:
        return button in self._runtime.input_state.mouse_buttons_down

    def is_mouse_clicked(self, button: int = 0) -> bool:
        # True só no frame do clique
        return button in self._runtime.input_state.mouse_buttons_clicked

    def get_gamepad(self, controller_id: int = 0) -> dict:
        return self._runtime.input_state.get_gamepad(controller_id)

    #cenas

    def change_scene(self, scene_name: str) -> None:
        # a troca acontece no fim do tick
        self._runtime.queue_scene_change(scene_name)

    def get_current_scene(self) -> str:
        return self._runtime.current_scene_name

    def reload_scene(self) -> None:
        self._runtime.queue_scene_change(self._runtime.current_scene_name)

    #comunicação entre entidades

    def send_message(self, entity_ids: list[str], message_name: str, data: Any = None) -> None:
        for entity_id in entity_ids:
            self._runtime.scene_runtime.send_message_to(entity_id, message_name, data)

    def broadcast_message(self, message_name: str, data: Any = None) -> None:
        # manda pra todas as entidades inscritas nessa mensagem
        self._runtime.scene_runtime.broadcast(message_name, data)

    # controle

    def pause_game(self) -> None:
        self._runtime.paused = True

    def resume_game(self) -> None:
        self._runtime.paused = False

    def quit_game(self) -> None:
        self._runtime.running = False

    # estado global

    @property
    def game_state(self) -> dict[str, Any]:
        # dicionário compartilhado por todas as cenas durante a sessão
        # útil pra guardar score, itens coletados, etc.
        # ex: ctx.game_state["score"] += 10
        return self._runtime.game_state
