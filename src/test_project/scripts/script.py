"""
script.py
---------
Hooks da entidade "player".
"""
 
 
def initialize(ctx, arg):
    """Chamado quando a entidade aparece na cena (on_spawn)."""
    print("Player spawnou!")
 
 
def on_clicked(ctx, arg):
    """Chamado quando a entidade é clicada (on_click) - ainda não disparado automaticamente."""
    print("Player foi clicado!")
 
 
def on_tick(ctx, arg):
    """Chamado a cada frame. Detecta manualmente se o clique caiu dentro do quadrado."""
    if not ctx.is_mouse_clicked(1):  # botão esquerdo
        return
 
    mx, my = ctx.get_mouse_position()
    props = ctx.get_entity_properties("my_player_1")
 
    if props is None:
        return
 
    dentro_x = props["x"] <= mx <= props["x"] + props["width"]
    dentro_y = props["y"] <= my <= props["y"] + props["height"]
 
    if dentro_x and dentro_y:
        print("Você acertou o quadrado!")
    else:
        print("Errou o quadrado")
