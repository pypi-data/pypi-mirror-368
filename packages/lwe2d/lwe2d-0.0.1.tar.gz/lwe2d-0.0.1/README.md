# LWE2D

LWE2D is a lightweight 2D game engine built using Pygame.  
It is designed to be simple, minimal, and easy to extend, it is also open-source so you can customize or make new things with it.

## Features
- Lightweight core for easy understanding and customization
- Built-in renderer for drawing text and images
- Basic input handling for keyboard and mouse
- Adjustable target FPS for smooth gameplay
- Boot splash system for branding your projects

## Getting Started
1. Install Python 3.9 or newer.
2. Install Pygame:
  ```bash
  pip install pygame
  ```
3. Clone the repository and run an example:
  ```bash
  python -m src.main
  ```

## Example/Quick Start

```python
from lwe2d.engine import Engine

engine = Engine()
engine.init(800, 600, "My LWE2D Game")
engine.set_target_fps(60)

while not engine.window_should_close():
    engine.begin_drawing()
    engine.renderer.clear((30, 30, 30))

    engine.renderer.draw_circle(400, 300, 50, (255, 0, 0))
    engine.renderer.draw_square(200, 200, 100, (0, 255, 0))

    engine.end_drawing()

engine.close_window()
```

## Why LWE2D

LWE2D is built for simplicity and speed. It focuses on giving you just the essential tools needed to make a game without unnecessary complexity. The engine is small enough to understand in a short time, yet flexible enough to expand with your own features. Whether you are experimenting with game ideas, learning how game loops work, or building a small project, LWE2D provides a clean and minimal foundation to start from.

---

## Cheatsheet

### Engine
```python
engine.init(width, height, title)       # Create a window and initialize LWE2D
engine.set_target_fps(fps)              # Limit the frame rate
engine.window_should_close()            # Returns True if the window should close
engine.begin_drawing()                  # Start drawing for the frame
engine.end_drawing()                    # End drawing and update the screen
engine.close_window()                   # Close the window and quit
```

### Input
```python
engine.is_key_down("w")                  # True while key is held down
engine.is_key_pressed("space")           # True only on the frame the key is pressed
engine.is_mouse_button_down(1)           # True while mouse button is held down
engine.is_mouse_button_pressed(1)        # True only when button is first clicked
engine.get_mouse_position()              # (x, y) position of the mouse
```

### Drawing
```python
renderer.clear((r, g, b))                 # Clear screen with color
renderer.draw_circle(x, y, radius, color, width)  
renderer.draw_square(x, y, size, color, width)  
renderer.draw_triangle(p1, p2, p3, color, width)  
renderer.render_text_or_image(obj, rect)  # Draw text or images
```

---

## Roadmap

### Completed
- [x] Circle, square, and triangle drawing functions
- [x] Keyboard and mouse input handling
- [x] Boot splash system

### Next Release Goals
- [ ] Rectangle, line, and polygon drawing
- [ ] Image loading and drawing
- [ ] Basic sprite animation

### Future Plans
- [ ] Audio playback
- [ ] Scene management
- [ ] Collision detection helpers
- [ ] Basic UI elements
- [ ] Save and load game data
- [ ] Expanded documentation
- [ ] Sample games