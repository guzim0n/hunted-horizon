import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,groups,sprite_type,id,surface=pygame.Surface((TILESIZE,TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.id = id

        if sprite_type == 'object':
            self.rect = self.image.get_rect(topleft=(pos[0],pos[1]-TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft = pos)

        self.hitbox = self.rect.inflate(0,-10)
        self.notice_radius = None

        if sprite_type == 'interactable':
            if int(self.id) == 17:
                self.response = 'Level 3'
            if int(self.id) == 18:
                self.response = 'Level 2'
            if int(self.id) == 19:
                self.response = 'Level 1'

        if sprite_type == 'object':
            for objectid,objectresponse in interactable_objects.items():
                if int(self.id) == objectid:
                    self.notice_radius = self.hitbox.inflate(50,100)
                    self.response = objectresponse
                