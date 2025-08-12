import pygame

class Renderer:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
    
    def clear(self, color: tuple[int, int, int] = (0, 0, 0)):
        self.surface.fill(color)
    
    def render_rect(self, color, rect):
        pygame.draw.rect(self.surface, color, rect)
    
    def render_surface(self, surface, rect):
        self.surface.blit(surface, rect)
    

    def draw_circle(self, x, y, radius, color=(255, 255, 255), width=0):
        """
        Draws a circle at (x, y) with the given radius.
        width=0 means filled circle, otherwise outline thickness.
        """
        pygame.draw.circle(self.surface, color, (x, y), radius, width)
    
    def draw_square(self, x, y, size, color=(255, 255, 255), width=0):
        """
        Draws a square with top-left corner at (x, y).
        width=0 means filled square, otherwise outline thickness.
        """
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(self.surface, color, rect, width)
    
    def draw_triangle(self, point1, point2, point3, color=(255, 255, 255), width=0):
        """
        Draws a triangle from 3 points.
        Example: draw_triangle((100,100), (150,50), (200,100))
        width=0 means filled, otherwise outline thickness.
        """
        pygame.draw.polygon(self.surface, color, [point1, point2, point3], width)