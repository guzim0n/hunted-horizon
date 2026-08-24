import pygame
from settings import *

class UI:
    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

    def show_health(self,current):
        self.health_img = pygame.image.load(f'../graphics/health/{current}.png').convert_alpha()
        self.display_surface.blit(self.health_img,(10,10))

    def display(self,player):
        if game_mode.mode[:5] == 'level':
            self.show_health(player.health)
