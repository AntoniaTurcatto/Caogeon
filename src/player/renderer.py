"""
renderer.py
-----------
Desenha o RenderData/RenderEntity produzidos pelo runtime a cada tick.
 
O runtime entrega apenas *caminhos relativos a raiz do projeto*
(background_path, sprite_path), nao Surfaces prontas e nao caminhos
absolutos. O renderer junta esses caminhos com project_root antes de
carregar do disco, e cacheia o resultado.
"""
 
from __future__ import annotations
 
from pathlib import Path
 
import pygame
 
from runtime.loop.render_data import RenderData, RenderEntity
 
 
class Renderer:
    """
    Desenha um frame em *screen* a partir de um RenderData.
 
    Parameters
    ----------
    screen:
        A surface pygame criada pela GameWindow.
    project_root:
        Pasta raiz do projeto (onde fica project.json). Os caminhos de
        sprite/background do RenderData sao relativos a essa pasta.
    """
 
    _FALLBACK_COLOR = (0, 0, 0)  # preto, quando nao ha background
 
    def __init__(self, screen: pygame.Surface, project_root: str | Path) -> None:
        self._screen = screen
        self._project_root = Path(project_root)
        self._image_cache: dict[str, pygame.Surface] = {}
 
    def render(self, data: RenderData) -> None:
        """Limpa a tela e desenha a cena descrita por *data*."""
        self._draw_background(data.background_path)
        self._draw_entities(data.entities)
 
    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------
 
    def _resolve_path(self, relative_path: str) -> Path:
        """Junta um caminho relativo do projeto com a raiz do projeto."""
        return self._project_root / relative_path
 
    def _load_image(self, path: str) -> pygame.Surface | None:
        """Carrega uma imagem do disco, com cache por caminho."""
        if not path:
            return None
        if path not in self._image_cache:
            full_path = self._resolve_path(path)
            try:
                self._image_cache[path] = pygame.image.load(str(full_path)).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"[Renderer] falhou ao carregar '{full_path}': {e}")
                return None
        return self._image_cache[path]
 
    def _draw_background(self, background_path: str) -> None:
        surface = self._load_image(background_path)
        if surface is None:
            self._screen.fill(self._FALLBACK_COLOR)
        else:
            scaled = pygame.transform.scale(
                surface, (self._screen.get_width(), self._screen.get_height())
            )
            self._screen.blit(scaled, (0, 0))
 
    def _draw_entities(self, entities: list[RenderEntity]) -> None:
        # a lista ja vem ordenada por z_index pelo runtime
        for entity in entities:
            surface = self._load_image(entity.sprite_path)
            if surface is None:
                continue
 
            # redimensiona para o tamanho base da entidade
            scaled = pygame.transform.scale(surface, (entity.width, entity.height))
 
            # aplica escala
            if entity.scale_x != 1.0 or entity.scale_y != 1.0:
                new_w = max(1, int(entity.width * entity.scale_x))
                new_h = max(1, int(entity.height * entity.scale_y))
                scaled = pygame.transform.scale(scaled, (new_w, new_h))
 
            # aplica flip
            if entity.flip_h or entity.flip_v:
                scaled = pygame.transform.flip(scaled, entity.flip_h, entity.flip_v)
 
            # aplica rotacao
            if entity.rotation != 0:
                scaled = pygame.transform.rotate(scaled, entity.rotation)
 
            # recentraliza apos transformacoes (rotacao muda o tamanho do retangulo)
            rect = scaled.get_rect(
                center=(entity.x + entity.width / 2, entity.y + entity.height / 2)
            )
            self._screen.blit(scaled, rect.topleft)
