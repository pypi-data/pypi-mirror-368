from .engine import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

engine = Engine()
engine.init(WINDOW_WIDTH, WINDOW_HEIGHT, "Player Example")

engine.set_target_fps(60)

pos = Vec2(100, 100)
speed = Vec2(0, 0)

player = Entity(pos.x, pos.y, 50, 50, (255, 0, 0))

while not engine.window_should_close():
    engine.begin_drawing()

    if engine.is_key_down("w"):
        player.rect.y -= 3
    if engine.is_key_down("s"):
        player.rect.y += 3
    if engine.is_key_down("a"):
        player.rect.x -= 3
    if engine.is_key_down("d"):
        player.rect.x += 3

    player.clamp(WINDOW_WIDTH, WINDOW_HEIGHT)
    engine.renderer.render_rect((255, 0, 0), player)

    engine.end_drawing()
engine.close_window()