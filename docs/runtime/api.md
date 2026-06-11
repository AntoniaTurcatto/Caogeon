### Entidades

`api.spawn_entity(entity_name: str, x: float, y: float)`

`api.destroy_entity(entity_id: str)` ao fim do tick

`api.get_entity_properties(entity_id: str) -> dict | None`

`api.get_entities_by_name(entity_name: str) -> list[str]`
Lista os IDs de todas as entidades ativas do tipo especificado.

`api.get_entities_in_area(x, y, w, h) -> list[str]`
Retorna IDs das entidades cuja hitbox intersecta a área fornecida.

`api.set_entity_visible(entity_id, visible: bool)`
Liga/desliga a renderização da entidade (a lógica continua rodando).

`api.set_entity_z_index(entity_id, z: int)`
Define a ordem de desenho (camada).

`api.get_entity_count() -> int`
Número total de entidades ativas na cena.

‌

### movimentação

`api.set_position(entity_id, x, y)` absoluto

`api.move_entity(entity_id, dx, dy) relativo a posição atual`

`api.get_position(entity_id) -> tuple[float, float]`

`api.set_rotation(entity_id, angle_degrees)`

`api.set_scale(entity_id, scale_x, scale_y)`
Escala do sprite (1.0 = tamanho original).

`api.flip_entity(entity_id, horizontal: bool, vertical: bool)`
Espelha o sprite.

‌

### física

`api.set_velocity(entity_id, vx, vy)`

### io

`api.is_key_down(key_name: str) -> bool`
Tecla está pressionada (ex.: `"space"`, `"a"`, `"left"`).

`api.is_key_pressed(key_name: str) -> bool`
Tecla foi pressionada neste frame (borda de subida).

`api.is_key_released(key_name: str) -> bool`
Tecla foi solta neste frame.

`api.get_mouse_position() -> tuple[float, float]`
Posição do mouse no mundo (considerando câmera).

`api.is_mouse_down(button=0) -> bool`
Botão do mouse está pressionado (0=esquerdo, 1=direito, 2=meio).

`api.is_mouse_clicked(button=0) -> bool`
Clique único ocorrido neste frame.

`api.get_gamepad(controller_id=0) -> dict`
Estado de eixos e botões de um controle.

### cenas

`api.change_scene(scene_name: str)`

`api.get_current_scene() -> str`

`api.reload_scene()`

### comunicação entre entidades

`api.send_message(entities_id: dict[str], message_name: str, data=None)`

Envia uma mensagem para entidades específicas, disparando um handler `on_message` no script dela

`api.broadcast_message(message_name: str, data=None)`

Envia a mensagem para todas as entidades ativas.

### geral do jogo

`api.pause_game()` / `api.resume_game()`
Pausa/continua o update das entidades (apenas UI continua).

`api.quit_game()`

finaliza processo

‌

### variável (dict) de variaveis globais do jogo

`api.game_state`

(exemplo de uso: `api.game_state['score'] += 10`)
