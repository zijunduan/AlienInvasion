import pygame
from pygame.sprite import Sprite
import os
import sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class Alien(Sprite):
    def __init__(self,ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image=pygame.image.load(resource_path("images/alien.bmp"))
        self.rect=self.image.get_rect()
        self.rect.x=self.rect.width
        self.rect.y=self.rect.height
        self.x=float(self.rect.x)
    def check_edges(self):
        screen_rect=self.screen.get_rect()
        return (screen_rect.right <= self.rect.right) or (self.rect.left<0)
    def update(self):
        self.x+=self.settings.alien_speed*self.settings.fleet_direction
        self.rect.x=self.x
