from dataclasses import dataclass, field


@dataclass
class InputState:
    # guarda o estado de input do frame atual
    # o player empurra os eventos aqui antes de cada tick
    # o runtime nunca acessa pygame/raylib diretamente, só lê daqui
    #
    # keys_down    -> tecla segurada (contínuo)
    # keys_pressed -> pressionada neste frame (borda de subida)
    # keys_released -> solta neste frame (borda de descida)

    keys_down: set[str] = field(default_factory=set)
    keys_pressed: set[str] = field(default_factory=set)
    keys_released: set[str] = field(default_factory=set)

    mouse_x: float = 0.0
    mouse_y: float = 0.0
    mouse_buttons_down: set[int] = field(default_factory=set)
    mouse_buttons_clicked: set[int] = field(default_factory=set)

    gamepads: dict[int, dict] = field(default_factory=dict)  # id -> {axes, buttons}

    def start_frame(self) -> None:
        # limpa os eventos de borda do frame anterior
        # o player chama isso antes de processar os eventos novos
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_buttons_clicked.clear()

    def press_key(self, key_name: str) -> None:
        if key_name not in self.keys_down:
            self.keys_pressed.add(key_name)
        self.keys_down.add(key_name)

    def release_key(self, key_name: str) -> None:
        if key_name in self.keys_down:
            self.keys_released.add(key_name)
        self.keys_down.discard(key_name)

    def press_mouse_button(self, button: int) -> None:
        # 0 = esquerdo, 1 = direito
        if button not in self.mouse_buttons_down:
            self.mouse_buttons_clicked.add(button)
        self.mouse_buttons_down.add(button)

    def release_mouse_button(self, button: int) -> None:
        self.mouse_buttons_down.discard(button)

    def move_mouse(self, x: float, y: float) -> None:
        self.mouse_x = x
        self.mouse_y = y

    def update_gamepad(self, controller_id: int, axes: dict, buttons: dict) -> None:
        self.gamepads[controller_id] = {"axes": axes, "buttons": buttons}

    def get_gamepad(self, controller_id: int = 0) -> dict:
        # retorna estado vazio se o controle não tiver conectado
        return self.gamepads.get(controller_id, {"axes": {}, "buttons": {}})
