from dataclasses import dataclass


@dataclass
class RenderEntity:
    # snapshot de uma entidade pra o player desenhar
    # o runtime monta isso a cada frame e entrega pro player

    id: str
    entity_name: str
    sprite_path: str
    x: float
    y: float
    width: int
    height: int
    z_index: int
    rotation: float
    scale_x: float
    scale_y: float
    flip_h: bool
    flip_v: bool


@dataclass
class RenderData:
    # tudo que o player precisa pra desenhar o frame atual
    # se background_path for vazio, a cena não tem background — renderiza preto

    scene_name: str
    background_path: str
    window_title: str
    window_width: int
    window_height: int
    entities: list[RenderEntity]
    paused: bool
