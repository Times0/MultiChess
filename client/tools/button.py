from tools.super import EasyObject

import pygame as pg

pg.font.init()
FONT = pg.font.Font(None, 25)


class EasyButton(EasyObject):
    def __init__(self):
        super().__init__()
        self.hover = False
        self.clicked = False

    def tick(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.tick(event.pos):
                    self.clicked = True

        mouse_pos = pg.mouse.get_pos()
        if self.tick(mouse_pos):
            self.hover = True
        else:
            self.hover = False


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
    def __init__(self, image_idle, image_working, image_hover, img_success):
        super().__init__(image_idle)
        self.image_idle = image_idle
        self.image_working = image_working
        self.image_hover = image_hover
        self.img_success = img_success

        self.isWorking = False
        self.isSucces = False

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        if self.isSucces:
            image = self.img_success
        elif self.isWorking:
            image = self.image_working
        elif self.hover:
            image = self.image_hover

        else:
            image = self.image_idle

        screen.blit(image, self.rect)

    def check_thread(self, thread, cond):
        if not thread:
            self.idle()
            return
        if thread.is_alive():
            self.working()
            if cond:
                print("success")
                self.success()
        else:
            self.idle()

    def working(self):
        self.isWorking = True

    def idle(self):
        self.isWorking = False
        self.isSucces = False

    def success(self):
        self.isSucces = True
