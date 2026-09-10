import pygame

class Notice_Bubble(pygame.sprite.Sprite):
    def __init__(self,player,groups):
        super().__init__(groups)

        self.animation = ['0','1','2','3']
        self.frame_index = 0
        self.animation_speed = 0.025

        self.direction = player.direction
        self.player = player
        self.player_top = player.rect.midtop

        self.image = pygame.image.load('../graphics/notice/0.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=self.player_top)

    def follow_player(self,player):
        if self.direction != [0,0]:
            self.player_top = player.rect.midtop
            self.rect.midbottom = self.player_top

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animation):
            self.frame_index = 0
        full_path = f'../graphics/notice/{self.animation[int(self.frame_index)]}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

    def update(self):
        self.follow_player(self.player)
        self.animate()
