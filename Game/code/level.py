import pygame
from settings import *
from tile import Tile
from player import Player
from support import *
from weapon import Weapon
from interact import Notice_Bubble
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from debug import debug

class Level:
    def __init__(self):
        
        # Get display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.interactable_sprites = pygame.sprite.Group()
        self.fall_sprites = pygame.sprite.Group()

        # Attack Sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Notice Sprite
        self.current_notice = None

        # Sprite setup
        self.current_mode = game_mode.mode
        self.create_map()

        # User Interface
        self.ui = UI()

        # Particles
        self.animation_player = AnimationPlayer()

    def create_map(self):
        graphics = {
            'details': import_folder('../graphics/details'),
            'objects': import_folder('../graphics/objects')
        }
        
        map_layouts = {
            'mainmap': {'boundary': import_csv_layout('../map/mainmap/mainmap_Wallblocks.csv'),
                        'interactable': import_csv_layout('../map/mainmap/mainmap_Interactable.csv'),
                        'detail': import_csv_layout('../map/mainmap/mainmap_BigDetails.csv'),
                        'object': import_csv_layout('../map/mainmap/mainmap_Objects.csv'),
                        'entities': import_csv_layout('../map/mainmap/mainmap_Entities.csv')},
            'level1': {'boundary': import_csv_layout('../map/level1/level1_Wallblocks.csv'),
                        'detail': import_csv_layout('../map/level1/level1_BigDetails.csv'),
                        'object': import_csv_layout('../map/level1/level1_Objects.csv'),
                        'fallblock': import_csv_layout('../map/level1/level1_Fallblocks.csv'),
                        'entities': import_csv_layout('../map/level1/level1_Entities.csv')}
        }

        for map,layouts in map_layouts.items():
            if map == game_mode.mode:
                current_layouts = layouts
    
        for style,layout in current_layouts.items():  # Items function retrieves the key and value pair
            for row_index,row in enumerate(layout):  # Enumerate returns row index number for each row as row_index
                for col_index,col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible',col)  # col is the actual value of the tile
                        if style == 'fallblock':
                            Tile((x,y),[self.fall_sprites],'fallblock',col)
                        if style == 'interactable':
                            Tile((x,y),[self.interactable_sprites],'interactable',col)
                        if style == 'detail':
                            surf = graphics['details'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'detail',col,surf)
                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',col,surf)
                        if style == 'entities':
                            if col == '42':
                                self.player = Player(
                                (x,y),
                                [self.visible_sprites],
                                self.obstacle_sprites,
                                self.interactable_sprites,
                                self.fall_sprites,
                                self.create_attack,
                                self.destroy_attack,
                                self.notice)
                            else:
                                if col == '39': monster_name = 'slime'
                                elif col == '40': monster_name = 'cyclops'
                                else: monster_name = 'raccoon'
                                Enemy(
                                    monster_name,
                                    (x,y),
                                    [self.visible_sprites,self.attackable_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player)

    def reload_map(self):
        if self.current_mode != game_mode.mode:
            for sprite in self.visible_sprites:
                sprite.kill()
            for sprite in self.obstacle_sprites:
                sprite.kill()
            for sprite in self.interactable_sprites:
                sprite.kill()
            for sprite in self.fall_sprites:
                sprite.kill()
            
            self.current_mode = game_mode.mode
            self.visible_sprites = YSortCameraGroup()
            self.create_map()

    def create_attack(self):
        self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        target_sprite.get_damage(self.player)

    def damage_player(self,attack_type):
        if self.player.vulnerable:
            self.player.change_health('lose')
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

    def notice(self):
        if self.player.noticing and self.current_notice == None:
           self.current_notice = Notice_Bubble(self.player,[self.visible_sprites])
        elif self.current_notice and not self.player.noticing:
            self.current_notice.kill()
            self.current_notice = None
        
        if self.current_notice:
            self.current_notice.update()

    def run(self):
        # Update + draw game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        self.ui.display(self.player)
        self.reload_map()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        
        # General setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Floor Creation
        self.floor_surf = pygame.image.load(f'../graphics/tilemap/{game_mode.mode}_ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))

    def custom_draw(self,player):
            # Getting offset
            self.offset.x = player.rect.centerx - self.half_width
            self.offset.y = player.rect.centery - self.half_height

            # Drawing the Floor
            floor_offset_pos = self.floor_rect.topleft - self.offset
            self.display_surface.blit(self.floor_surf,floor_offset_pos)

            # Drawing the Sprites
            for sprite in sorted(self.sprites(),key=lambda sprite: sprite.rect.centery):
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image,offset_pos)
    
    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
        #debug(enemy_sprites[14].can_attack)
