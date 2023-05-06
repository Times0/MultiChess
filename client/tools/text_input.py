from tools.super import EasyObject

import pygame as pg

pg.font.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 25)


class InputBox(EasyObject):

    def __init__(self, text='', font: pg.font.Font = FONT, width: int = None):
        """
        if width is None, then the width will be the width of the text
        """
        super().__init__()
        self.color = COLOR_INACTIVE
        self.text = text
        self.active = False
        self.font = font
        self.max_width = width

        if width:
            self.rect = pg.Rect(0, 0, width, 20)
        else:
            self.rect = pg.Rect(0, 0, 0, 20)  # width will be changed when rendering

        # Render the text to get the height
        fake_render = self.font.render("A", True, self.color)
        self.rect.h = fake_render.get_height() + 10

        self._render()

    def handle_event(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

            if not self.active:
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        self._render()

    def _render(self):
        self.txt_surface = self.font.render(self.text, True, self.color)
        if not self.max_width:
            self.rect.width = self.txt_surface.get_width() + 10

    def draw(self, screen, x, y):
        self.rect.x = x
        self.rect.y = y

        # Background surface
        surface = pg.Surface((self.rect.w, self.rect.h))
        surface.fill((255, 255, 255))
        surface.set_alpha(50)  # transparency value -> 0: transparent; 255: opaque

        # Blit the text.
        screen.blit(surface, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text
