from pico2d import load_image, get_time
from worldmap import *
from sdl2 import *

class move:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        pass
    def exit(self):
        pass
    def do(self):
        pass
    def draw(self, e):
        pass

class character:
    def __init__(self):
        self.image = load_image('resource/character/character_sprites_vertical_merged.png')
        self.x = WorldMap.width/2
        self.y = WorldMap.height/2
        self.frame = 0
        self.updown_dir = 1
        self.face_dir = 1
        self.dir = 0
        self.max_dash = 2
        self.can_dash = self.max_dash
        self.weapon_type = katana # 카타나 또는 대검
        self.STR = 20
        self.critical = 0.05
        self.critical_damage = 1.5

        self.idle = Idle(self)
        self.move = Move(self)
        self.attack = Attack(self)

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))