import pygame
from settings import *
from support import import_folder
from entity import Entity
from debug import debug

class Player(Entity):
    def __init__(self,pos,groups,obstacle_sprites,interactable_sprites,fall_sprites,create_attack,destroy_attack,notice):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0,-26)
        self.fall_hitbox = self.rect.inflate(-50,-62)
        self.fall_hitbox.bottom = self.hitbox.bottom

        self.width = 64
        self.height = 64

        # Graphic Setup
        self.import_player_assets()
        self.status = 'down'

        # Player movement
        self.speed = 5

        self.current_ground = self.hitbox.y
        self.gravity = 0.8
        self.jump_force = -15
        self.vertical_speed = 0
        self.jumping = False
        self.down = False
        self.jump_released = True
        self.jump_pos = None
        self.falling = False

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # Weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon = list(weapon_data.keys())[0]

        # Notice + Interacting
        self.notice = notice
        self.noticing = False
        self.notice_id = None
        self.notice_response = None

        self.obstacle_sprites = obstacle_sprites
        self.interactable_sprites = interactable_sprites
        self.fall_sprites = fall_sprites

        # Stats
        self.health = 4
        self.coins = 123

        # Damage Timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # Repositioning
        self.spawn_pos = self.hitbox.center
        self.repos = None

    def import_player_assets(self):
        character_path = '../graphics/player/'
        self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
            'up_idle':[], 'down_idle':[], 'left_idle':[], 'right_idle':[],
            'up_attack':[], 'down_attack':[], 'left_attack':[], 'right_attack':[],
            'up_jump':[], 'down_jump':[], 'left_jump':[], 'right_jump':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking and not self.falling:
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.current_ground = self.hitbox.y
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.current_ground = self.hitbox.y
                self.down = True
                self.status = 'down'
            else:
                self.direction.y = 0
                self.down = False

            if keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE] and self.jump_released:
                self.jump()
                self.jump_released = False

            if not keys[pygame.K_SPACE]:
                self.jump_released = True

            if keys[pygame.K_j] and not self.jumping:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            if keys[pygame.K_k]:
                print('block')

            if keys[pygame.K_l]:
                self.interact()

    def get_status(self):
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status and not 'jump' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0   # Stops player from moving while attacking
            self.direction.y = 0   # ^
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_attack')
                elif 'jump' in self.status:
                    self.status = self.status.replace('_jump','_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','')

        if self.jumping:
            if not 'jump' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_jump')
                elif 'attack' in self.status:
                    self.status = self.status.replace('_attack','_jump')
                else:
                    self.status = self.status + '_jump'
        else:
            if 'jump' in self.status:
                self.status = self.status.replace('_jump','')

    def check_fall(self):
        self.fall_hitbox.midbottom = self.hitbox.midbottom

        if self.fall_hitbox.collidelist(list(self.fall_sprites)) != -1 and not self.jumping:
            self.falling = True
            self.direction.x = 0
            self.direction.y = 0

    def check_notice(self):
        self.noticing = False
        self.notice_id = None
        self.notice_response = None
        for sprite in self.interactable_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                self.noticing = True
                self.notice_id = sprite.id
                self.notice_response = sprite.response

        for object in self.obstacle_sprites:
            if object.notice_radius:
                if object.notice_radius.colliderect(self.hitbox):
                    self.noticing = True
                    self.notice_id = object.id
                    self.notice_response = object.response

    def interact(self):
        if self.noticing and self.notice_id:
            print(self.notice_response)
            if int(self.notice_id) == 19:
                game_mode.mode = 'level1'

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if (current_time-self.attack_time) >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if not self.vulnerable:
            if (current_time - self.hurt_time) >= self.invulnerability_duration:
                self.vulnerable = True

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vertical_speed = self.jump_force
            self.jump_pos = self.hitbox.center

    def apply_gravity(self):
        if self.jumping and self.down:
            self.vertical_speed += self.gravity
            self.hitbox.y -= self.vertical_speed

            if self.hitbox.y <= self.current_ground:
                self.hitbox.y = self.current_ground
                self.jumping = False
                self.vertical_speed = 0

        elif self.jumping:
            self.vertical_speed += self.gravity
            self.hitbox.y += self.vertical_speed

            if self.hitbox.y >= self.current_ground:
                self.hitbox.y = self.current_ground
                self.jumping = False
                self.vertical_speed = 0
            
    def fall(self):
        if self.falling:
            pos = self.rect.topleft
            if self.width > 0 and self.height > 0:
                self.image = pygame.transform.scale(self.image,(int(self.width),int(self.height)))
                self.rect = self.image.get_rect(topleft = pos)
                self.width -= 1.5
                self.height -= 1.5
                self.hitbox.y += 3
            else:
                self.falling = False
                self.change_health('lose')
                if self.jump_pos:
                    self.hitbox.center = self.jump_pos
                else:
                    self.hitbox.center = self.spawn_pos
                self.width = 64
                self.height = 64

    def change_health(self,change):
        if change == 'lose':
            if self.health > 0:
                self.health -= 1
                if self.health == 0:
                    print('Game Over')
        if change == 'gain':
            self.health = 4

    def animate(self):
        animation = self.animations[self.status]

        # Looping over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        # Flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)


    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
        self.apply_gravity()
        self.check_notice()
        self.notice()
        self.check_fall()
        self.fall()
        
        