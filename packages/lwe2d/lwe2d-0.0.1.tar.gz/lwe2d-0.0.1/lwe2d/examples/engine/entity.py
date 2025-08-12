import pygame

class Entity:
    def __init__(self, x: float, y: float, w: int, h: int, color: tuple[int, int, int]) -> None:
        self.position = pygame.Vector2(x, y)
        self.size = pygame.Vector2(w, h)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        self.color = color
    
    def clamp(self, width: int, height: int):
        self.rect.clamp_ip(pygame.Rect(0, 0, width, height))
    
    def update(self, delta: float):
        pass

    def draw(self, renderer):
        renderer.render_rect(self.color, self.rect)