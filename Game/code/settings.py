# Game setup
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

class MODE:
    def __init__(self):
        self.mode = 'mainmap'

game_mode = MODE()

# UI
UI_FONT = '../graphics/font/NormalFont.ttf'
UI_FONT_SIZE = 18
TEXT_COLOUR = '#EEEEEE'

weapon_data = {
    'sword': {'cooldown':100, 'damage':1, 'graphic':'../graphics/weapons/sword/full.png'}
}

interactable_objects = {
    23: 'Boss',
    32: 'Arcade',
    37: 'Trophies',
    43: 'Inspector',
    44: 'Old man',
    45: 'Villager 1',
    46: 'Villager 2'
}

monster_data = {
    'raccoon': {'health':4, 'damage':1, 'attack_type':'claw', 'attack_sound':'../audio/attack/claw.wav', 'speed':3, 'resistance':3, 'attack_radius':40, 'notice_radius':350},
    'cyclops': {'health':4, 'damage':1, 'attack_type':'stomp', 'attack_sound':'../audio/attack/stomp.wav', 'speed':2, 'resistance':3, 'attack_radius':60, 'notice_radius':350},
    'slime': {'health':3, 'damage':1, 'attack_type':'ice', 'attack_sound':'../audio/attack/ice.wav', 'speed':1, 'resistance':3, 'attack_radius':120, 'notice_radius':400}
}
