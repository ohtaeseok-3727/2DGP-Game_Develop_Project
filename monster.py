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
    image = None

    def __init__(self, x, y, monster_type='default'):
       pass

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
