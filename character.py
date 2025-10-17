from pico2d import load_image, get_time
from worldmap import *
from sdl2 import *
from state_machine import StateMachine

class Move:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        pass
    def exit(self):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Idle:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        self.character.dir = 1
        self.character.face_dir = 1
        self.character.updown_dir = -1
        pass
    def exit(self):
        pass
    def do(self):
        self.character.frame = (self.character.frame + 1) % 6
        pass
    def draw(self):
        if self.character.dir == 1 and self.character.updown_dir == -1:
            self.character.image.clip_draw(self.character.frame*18, 57, 18, 19, self.character.x, self.character.y, 54, 57)
        if self.character.dir == -1 and self.character.updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame*18, 57, 18, 19, 0, '',self.character.x, self.character.y, 54, 57)
        if self.character.dir == 1 and self.character.updown_dir == 1:
            self.character.image.clip_draw(self.character.frame*18, 76, 18, 19, self.character.x, self.character.y, 54, 57)
        if self.character.dir == -1 and self.character.updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame*18, 76, 18, 19, 0, '',self.character.x, self.character.y, 54, 57)
        pass

class Attack:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        pass
    def exit(self):
        pass
    def do(self):
        pass
    def draw(self):
        pass


class character:
    def __init__(self):
        self.image = load_image('resource/character/character_sprites_vertical_merged.png')
        self.x = WorldMap.width/2
        self.y = WorldMap.height/2
        self.frame = 0
        self.updown_dir = 0 # 1: up, -1: down
        self.face_dir = 0 # 1: right, -1: left
        self.dir = 0 # 1: right, -1: left
        self.max_dash = 2
        self.can_dash = self.max_dash
        self.weapon_type = 'katana' # 카타나 또는 대검
        self.STR = 20
        self.critical = 0.05
        self.critical_damage = 1.5

        self.idle = Idle(self)
        self.move = Move(self)
        self.attack = Attack(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {},
            self.move: {},
            self.attack: {}
        })

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))