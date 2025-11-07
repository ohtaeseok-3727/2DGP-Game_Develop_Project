from pico2d import *
import math
import game_framework
import game_world

PIXEL_PER_METER = (10.0 / 0.3)
MONSTER_SPEED_KMPH = 10.0
MONSTER_SPEED_MPM = (MONSTER_SPEED_KMPH * 1000.0 / 60.0)
MONSTER_SPEED_MPS = (MONSTER_SPEED_MPM / 60.0)
MONSTER_SPEED_PPS = (MONSTER_SPEED_MPS * PIXEL_PER_METER)


class Monster:
    images = {}
    def __init__(self, x, y, monster_type='blue_slime'):
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.frame = 0
        self.frame_time = 0
        self.fps = 10
        self.is_alive = True
        self.target = None

        if monster_type == 'small_blue_slime':
            self.hp = 50
            self.max_hp = 50
            self.damage = 5
            self.frame_width = 17
            self.frame_height = 12
            self.max_frames = 6
            self.detection_range = 150
            self.attack_range = 5
            self.speed_multiplier = 1.0

            if 'small_blue_slime' not in Monster.images:
                Monster.images['small_blue_slime'] = load_image('resource/monster/small_blue_slime_sprite_sheet.png')
            self.image = Monster.images['small_blue_slime']

        elif monster_type == 'blue_slime':
            self.hp = 100
            self.max_hp = 100
            self.damage = 10
            self.frame_width = 14
            self.frame_height = 33
            self.max_frames = 10
            self.detection_range = 200
            self.attack_range = 30
            self.speed_multiplier = 0.8

            if 'blue_slime' not in Monster.images:
                Monster.images['blue_slime'] = load_image('resource/monster/blue_slime_sprite_sheet.png')
            self.image = Monster.images['blue_slime']

        self.hit_cooldown = 0

    def set_target(self, target):
        pass
    def update(self, camera=None):
        pass

    def take_damage(self, damage):
         pass

    def die(self):
         pass

    def get_bb(self):
         pass

    def handle_collision(self, group, other):
         pass

    def draw(self, camera=None):
        pass
