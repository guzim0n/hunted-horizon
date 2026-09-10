import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
    def __init__(self,monster_name,pos,groups,obstacle_sprites,damage_player):
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # Graphics
        self.import_graphics(monster_name)
        self.status = 'idle_down'
        self.status_direction = 'down'
        self.image = self.animations[self.status][self.frame_index]

        # Movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0,-10)
        self.obstacle_sprites = obstacle_sprites

        # Stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # Player Interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player

        # Invincibilty Timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

    def import_graphics(self,name):
        self.animations = {'idle_up':[],'idle_down':[],'idle_right':[],'idle_left':[],
            'attack_up':[],'attack_down':[],'attack_right':[],'attack_left':[],
            'move_up':[], 'move_down':[], 'move_right':[], 'move_left':[]}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self,player):
        enemy_vec = pygame.math.Vector2(self.hitbox.center)
        player_vec = pygame.math.Vector2(player.hitbox.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()  # Gives vector of (0,0)

        return (distance,direction)

    def get_status(self,player):
        distance = self.get_player_distance_direction(player)[0]

        if self.direction[0] != 0 and self.direction[1] != 0:
            if abs(self.direction[0]) < abs(self.direction[1]):
                if self.direction[1] > 0:
                    self.status_direction = 'down'
                else:
                    self.status_direction = 'up'
            else:
                if self.direction[0] > 0:
                    self.status_direction = 'right'
                else:
                    self.status_direction = 'left'

        if distance <= self.attack_radius and self.can_attack:
            if self.status[:6] != 'attack':
                self.frame_index = 0
            self.status = f'attack_{self.status_direction}'
        elif distance <= self.notice_radius:
            self.status = f'move_{self.status_direction}'
        else:
            self.status = f'idle_{self.status_direction}'

    def actions(self,player):
        if self.status[:6] == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_type)
        elif self.status[:4] == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status[:6] == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)  # Full opacity

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if (current_time - self.attack_time) >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if (current_time - self.hit_time) >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self,player):
        if self.vulnerable:
            self.direction = self.get_player_distance_direction(player)[1]
            self.health -= weapon_data[player.weapon]['damage']
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self):
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self,player):
        self.get_status(player)
        self.actions(player)
