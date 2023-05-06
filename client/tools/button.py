from tools.super import EasyObject

import pygame as pg

pg.font.init()
FONT = pg.font.Font(None, 25)


class EasyButton(EasyObject):
    def __init__(self):
        super().__init__()

    def tick(self, pos):
        return self.rect.collidepoint(pos)


class ButtonRect(EasyButton):
    def __init__(self, w, h, color):
        super().__init__()
        self.w = w
        self.h = h
        self.color = color
        self.rect = pg.Rect(self.x, self.y, w, h)
        self.clicked = False
        self.surface = pg.Surface((w, h))
        self.surface.fill(color)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.surface, self.rect)


class ButtonImage(EasyButton):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.image, self.rect)


class ButtonThread(ButtonImage):
    def __init__(self, image_idle, image_working):
        super().__init__(image_idle)
        self.image_idle = image_idle
        self.image_working = image_working
        self.isWorking = False

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.image, self.rect)

    def check_thread(self, thread):
        if thread.is_alive():
            self.working()
        else:
            self.idle()

    def working(self):
        self.isWorking = True
        self.image = self.image_working

    def idle(self):
        self.isWorking = False
        self.image = self.image_idle
