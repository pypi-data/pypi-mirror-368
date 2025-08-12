import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")
import pygame, time
from .renderer import Renderer

class Engine:
    def init(self, width: int, height: int, game_title: str):
        print("ENGINE: Initializing...")

        pygame.init()

        self._should_close = False
        self.deltaTime = 0
        self.targetFPS = 0
        self.clock = pygame.time.Clock()
        with open("src/engine/engine-icon.png", 'rb') as icon:
            self.engine_icon = pygame.image.load(icon)

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption(game_title)
        pygame.display.set_icon(self.engine_icon)

        self.renderer = Renderer(self.window)

        self._keys_down = set()
        self._keys_pressed = set()
        self._mouse_down = set()
        self._mouse_pressed = set()
        
        print("ENGINE: Initialized")

        self.boot_splash()
    
    def window_should_close(self):
        self._process_events()
        return self._should_close
    
    def _process_events(self):
        self._keys_pressed.clear()
        self._mouse_pressed.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._should_close = True

            elif event.type == pygame.KEYDOWN:
                self._keys_down.add(event.key)
                self._keys_pressed.add(event.key)
            
            elif event.type == pygame.KEYUP:
                self._keys_down.discard(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_down.add(event.button)
                self._mouse_pressed.add(event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down.discard(event.button)
    
    
    def is_key_down(self, key_name):
        return pygame.key.key_code(key_name) in self._keys_down
    
    def is_key_pressed(self, key_name):
        return pygame.key.key_code(key_name) in self._keys_pressed

    def is_mouse_button_down(self, button):
        return button in self._mouse_down

    def is_mouse_button_pressed(self, button):
        return button in self._mouse_pressed

    def get_mouse_position(self):
        return pygame.mouse.get_pos()
    

    def set_target_fps(self, fps):
        self.targetFPS = fps
        print(f"ENGINE: Set target FPS to {fps}")
    
    def begin_drawing(self):
        self.renderer.clear()

    def end_drawing(self):
        pygame.display.flip()
        self.clock.tick(self.targetFPS)
    
    def close_window(self):
        pygame.quit()
        print("ENGINE: Window closed")


    def boot_splash(self, duration=2):
        print("ENGINE: Boot")
        self.renderer.clear((255, 255, 255))

        title_font = pygame.font.Font(None, 100)
        title_text = title_font.render("LWE2D", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() // 2 - 40))
        icon_rect = self.engine_icon.get_rect(center=(self.window.get_width() // 2, self.window.get_height() // 2 + 30))

        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            progress = elapsed / duration

            if progress >= 1.0:
                break

            title_surf = title_text.copy()
            icon_surf = self.engine_icon
            self.renderer.render_surface(title_surf, title_rect)
            self.renderer.render_surface(icon_surf, icon_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._should_close = True
                    return

            self.clock.tick(60)
