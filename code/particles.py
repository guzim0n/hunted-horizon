import pygame
from support import import_folder

class AnimationPlayer:
    def __init__(self):
        self.frames = {
            # Attacks
            'slash': import_folder('../graphics/particles/slash'),
            'claw': import_folder('../graphics/particles/claw'),
            'ice': import_folder('../graphics/particles/ice'),
            'stomp': import_folder('../graphics/particles/stomp')
        }
    
    def create_particles(self,animation_type,pos,groups):
        animation_frames = self.frames[animation_type]
        ParticleEffect(pos,animation_frames,groups)


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self,pos,animation_frames,groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()
