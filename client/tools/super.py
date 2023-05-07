import pygame as pg

class EasyObject:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

    def update_pos(self, x, y):
        self.rect.x += x
        self.rect.y += y
        self.x = x
        self.y = y
