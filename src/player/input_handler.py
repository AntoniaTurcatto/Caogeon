"""
input_handler.py
----------------
Traduz eventos pygame e escreve direto no InputState do runtime.

O runtime.input_state guarda: keys_down, keys_pressed, keys_released,
mouse_x, mouse_y, mouse_buttons_down, mouse_buttons_clicked.

O handler nao possui logica de jogo; ele so atualiza esse estado
a cada frame, e o runtime/scripts leem dali (via RuntimeAPI.is_key_held etc).
"""

from __future__ import annotations

import pygame


class InputHandler:
    """
    Atualiza o InputState do runtime a partir de eventos pygame.

    Parameters
    ----------
    input_state:
        O objeto runtime.input_state (ver runtime/io/input_state.py).
        Espera os atributos/metodos usados abaixo.
    """

    def __init__(self, input_state) -> None:
        self._state = input_state

    def begin_frame(self) -> None:
        """Limpa os conjuntos 'desse frame' (pressed/released/clicked)."""
        self._state.keys_pressed.clear()
        self._state.keys_released.clear()
        self._state.mouse_buttons_clicked.clear()

    def handle(self, event: pygame.event.Event) -> None:
        """Despacha *event* para o InputState correto."""
        if event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
            if key not in self._state.keys_down:
                self._state.keys_pressed.add(key)
            self._state.keys_down.add(key)

        elif event.type == pygame.KEYUP:
            key = pygame.key.name(event.key)
            self._state.keys_down.discard(key)
            self._state.keys_released.add(key)

        elif event.type == pygame.MOUSEMOTION:
            self._state.mouse_x, self._state.mouse_y = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._state.mouse_buttons_down.add(event.button)
            self._state.mouse_buttons_clicked.add(event.button)

        elif event.type == pygame.MOUSEBUTTONUP:
            self._state.mouse_buttons_down.discard(event.button)
