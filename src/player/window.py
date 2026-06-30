"""
window.py
---------
Cria e gerencia a janela do jogo.
O player nao contem logica de jogo; tudo passa pelo runtime
(tick, render, input_state).
"""
 
from __future__ import annotations
 
import pygame
 
from player.renderer import Renderer
from player.input_handler import InputHandler
 
 
class GameWindow:
    """
    Objeto principal do player.
 
    Usage::
 
        from core.managers import ProjectPaths
        from core.project_manager import ProjectManager
        from runtime.loop.game_loop import GameRuntime
        from player.window import GameWindow
 
        project_manager = ProjectManager()
        project_manager.load(ProjectPaths("caminho/do/projeto"))
        runtime = GameRuntime(project_manager, "caminho/do/projeto")
 
        window = GameWindow(runtime, "caminho/do/projeto")
        window.run()
    """
 
    def __init__(self, runtime, project_root: str) -> None:
        """
        Parameters
        ----------
        runtime:
            Uma instancia de GameRuntime ja carregada. A janela so chama:
            - runtime.tick(delta_time)   (avanca um frame)
            - runtime.render()           (snapshot RenderData do frame)
            - runtime.input_state        (escreve input recebido)
            - runtime.running            (flag de continuar rodando)
        project_root:
            Pasta raiz do projeto, usada pelo Renderer para resolver os
            caminhos relativos de sprite/background.
        """
        self._runtime = runtime
 
        pygame.init()
 
        # pega as dimensoes/titulo iniciais a partir do primeiro RenderData
        initial_data = runtime.render()
        self._screen = pygame.display.set_mode(
            (initial_data.window_width, initial_data.window_height)
        )
        pygame.display.set_caption(initial_data.window_title)
 
        self._clock = pygame.time.Clock()
 
        self._renderer = Renderer(self._screen, project_root)
        self._input_handler = InputHandler(runtime.input_state)
 
        self._running = False
 
    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
 
    def run(self) -> None:
        """Inicia o loop do jogo. Bloqueia ate a janela ser fechada."""
        self._running = True
        while self._running and self._runtime.running:
            delta_time = self._clock.tick(60) / 1000.0  # segundos desde o ultimo frame
 
            self._input_handler.begin_frame()
            self._process_events()
 
            self._runtime.tick(delta_time)
 
            render_data = self._runtime.render()
            self._renderer.render(render_data)
            pygame.display.flip()
 
        pygame.quit()
 
    def stop(self) -> None:
        """Solicita que o loop pare apos o frame atual."""
        self._running = False
 
    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------
 
    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            else:
                self._input_handler.handle(event)