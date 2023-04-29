import pygame


class TextButton(pygame.sprite.Sprite):
    def __init__(self, text, x, y, font, font_color):
        super().__init__()
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.text_surface = self.font.render(self.text, True, font_color)
        self.rect = self.text_surface.get_rect(topleft=(x, y))

    def tick(self) -> bool:
        return self.isMouseOn(pygame.mouse.get_pos())

    def isMouseOn(self, pos) -> bool:
        return self.rect.collidepoint(*pos)

    def draw(self, screen):
        screen.blit(self.text_surface, (self.x, self.y))
