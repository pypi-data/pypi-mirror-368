from .engine import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

engine = Engine()
engine.init(WINDOW_WIDTH, WINDOW_HEIGHT, "Shapes Example")

engine.set_target_fps(60)

while not engine.window_should_close():
    engine.begin_drawing()

    engine.renderer.draw_circle(200, 150, 50, color=(255, 0, 0))  # Red filled circle
    engine.renderer.draw_square(300, 100, 80, color=(0, 255, 0), width=5)  # Green square outline
    engine.renderer.draw_triangle((500, 300), (550, 200), (600, 300), color=(0, 255, 255))  # Cyan filled triangle

    engine.end_drawing()
engine.close_window()