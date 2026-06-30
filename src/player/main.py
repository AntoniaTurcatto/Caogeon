"""
main.py  (ponto de entrada do player)
-----------------------------
Carrega o projeto Caogeon e abre a janela do jogo
Usage::
    python -m player.main path/to/project_files/
"""

from __future__ import annotations

import sys
from pathlib import Path
from runtime.loader.loader import load_project #imports para funcionamento
from runtime.loop.game_loop import GameRuntime
from player.window import GameWindow

def main() -> None:
    if len(sys.argv) < 2: #Verifica o que foi digitado na linha de comando
        print("Usage: python -m player.main <project_path>")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve() #transforma o que o usuário digitou em um caminho
    if not project_path.exists(): #verifica se o caminho existe
        print(f"Project path not found: {project_path}")
        sys.exit(1)

    project_manager, _initial_scene = load_project(project_path) #carrega o projeto, ignorando o _initial_scene

    runtime = GameRuntime(project_manager, project_path) #Cria o motor do jogo. Nesse momento ele já carrega a cena e dispara o on_spawn das entidades.

    window = GameWindow(runtime, str(project_path)) #Cria a janela, passando o motor (pra rodar o jogo) e o caminho do projeto (pra achar as imagens).
    window.run()


if __name__ == "__main__":
    main()
