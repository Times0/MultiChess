import pygame as pg
import pygame.gfxdraw


from tools.super import EasyObject

pg.font.init()
FONT = pg.font.Font(None, 25)


class EasyButton(EasyObject):
    def __init__(self, onclick_f):
        super().__init__()
        self.hover = False
        self.clicked = False
        self.onclick_f = onclick_f

        self.surface = None
        self.surface_hover = None

    def tick(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.tick(event.pos):
                    self.clicked = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.clicked:
                    self.onclick_f()
                self.clicked = False

            if event.type == pg.MOUSEMOTION:
                self.hover = self.tick(event.pos)


class ButtonRect(EasyButton):
    def __init__(self, w, h, color, onclick_f):
        super().__init__(onclick_f)
        self.w = w
        self.h = h
        self.color = color

        self.surface = pg.Surface((w, h))
        self.surface.fill(color)
        self.update_surface_hover()

        self.rect = self.surface.get_rect()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        if self.hover:
            print("hover")
            screen.blit(self.surface_hover, self.rect)
        else:
            screen.blit(self.surface, self.rect)

    def update_surface_hover(self):
        # Same as surface but with a lighter color
        self.surface_hover = self.surface.copy()
        self.surface_hover.fill([min(255, c + 50) for c in self.color])


class ButtonImage(EasyButton):
    def __init__(self, image, onclick_f):
        super().__init__(onclick_f)
        self.image = image
        self.rect = self.image.get_rect()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.image, self.rect)


class IconImagePng(ButtonImage):
    def __init__(self, image, onclick_f):
        super().__init__(image, onclick_f)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        # if hover then blit a transparent rect behind the image
        if self.hover or self.clicked:
            pg.draw.rect(screen, (76, 80, 82, 100), self.rect, border_radius=5,)
        screen.blit(self.image, self.rect)


class ButtonThread(ButtonImage):
    def __init__(self, image_idle, image_working, image_hover, img_success, onclick_f):
        super().__init__(image_idle, onclick_f)
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

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.tick(event.pos):
                    self.clicked = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.clicked and not self.isWorking and not self.isSucces:
                    self.onclick_f()
                self.clicked = False

            if event.type == pg.MOUSEMOTION:
                self.hover = self.tick(event.pos)
