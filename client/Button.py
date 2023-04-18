import pygame

from constants import *


class Button:
    def __init__(self, defaultcolor, hovercolor, x, y, width, height, onclick, text, textcolor=RED):
        self.defaultcolor = defaultcolor
        self.hovercolor = hovercolor
        self.color = defaultcolor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.textcolordefault = textcolor
        self.textcolor = textcolor
        self.textcolorhover = textcolor
        self.onclick = onclick

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 45)
            text = font.render(self.text, True, self.textcolor)
            win.blit(text, (self.x + 8, self.y + (self.height / 2 - text.get_height() / 2)))

    def isMouseon(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

    def hover(self):
        self.color = self.hovercolor
        self.textcolor = self.textcolorhover

    def default(self):
        self.color = self.defaultcolor
        self.textcolor = self.textcolordefault
