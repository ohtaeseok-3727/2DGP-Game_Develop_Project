from pico2d import load_image, get_time
from worldmap import *
from sdl2 import *
from state_machine import StateMachine

def A_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def A_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a
def S_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s
def S_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_s
def D_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d
def D_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d
def W_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w
def W_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_w

class Move:
    def __init__(self, character):
        self.character = character
        self.fps = 15
        self.frame_time = 0
    def enter(self, e):
        self.frame_time = get_time()
        if A_down(e):
            self.character.key_state['A'] = True
        if D_down(e):
            self.character.key_state['D'] = True
        if W_down(e):
            self.character.key_state['W'] = True
        if S_down(e):
            self.character.key_state['S'] = True
        if A_up(e):
            self.character.key_state['A'] = False
        if D_up(e):
            self.character.key_state['D'] = False
        if W_up(e):
            self.character.key_state['W'] = False
        if S_up(e):
            self.character.key_state['S'] = False

        self.character.dir = 0
        self.character.updown_dir = 0

        if self.character.key_state['A']:
            self.character.dir = -1
        if self.character.key_state['D']:
            self.character.dir = 1
        if self.character.key_state['W']:
            self.character.updown_dir = 1
        if self.character.key_state['S']:
            self.character.updown_dir = -1

        if self.character.dir != 0:
            self.character.face_dir = self.character.dir
        if self.character.updown_dir != 0:
            self.character.face_updown_dir = self.character.updown_dir

        pass
    def exit(self, e):
        pass
    def do(self):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame + 1) % 8
            self.frame_time = get_time()

        self.character.x += self.character.dir * 5
        self.character.y += self.character.updown_dir * 5
        pass
    def draw(self):
        if self.character.dir == 1 and self.character.updown_dir == -1:
            self.character.image.clip_draw(self.character.frame * 18, 19, 18, 19, self.character.x, self.character.y,
                                           54, 57)
        if self.character.dir == -1 and self.character.updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 19, 18, 19, 0, 'h', self.character.x,
                                                     self.character.y, 54, 57)
        if self.character.dir == 1 and self.character.updown_dir == 1:
            self.character.image.clip_draw(self.character.frame * 18, 0, 18, 19, self.character.x, self.character.y,
                                           54, 57)
        if self.character.dir == -1 and self.character.updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 0, 18, 19, 0, 'h', self.character.x,
                                                     self.character.y, 54, 57)
        pass

class Idle:
    def __init__(self, character):
        self.character = character
        self.fps = 10
        self.frame_time = 0
    def enter(self, e):
        self.frame_time = get_time()
        pass
    def exit(self, e):
        pass
    def do(self):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame + 1) % 6
            self.frame_time = get_time()
        pass
    def draw(self):
        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(self.character.frame*18, 57, 18, 19, self.character.x, self.character.y, 54, 57)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame*18, 57, 18, 19, 0, 'h',self.character.x, self.character.y, 54, 57)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(self.character.frame*18, 38, 18, 19, self.character.x, self.character.y, 54, 57)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(self.character.frame*18, 38, 18, 19, 0, 'h',self.character.x, self.character.y, 54, 57)
        pass

class Attack:
    def __init__(self, character):
        self.character = character
    def enter(self, e):
        pass
    def exit(self, e):
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
        self.face_updown_dir = -1 # 1: up, -1: down
        self.face_dir = -1 # 1: right, -1: left
        self.dir = 0 # 1: right, -1: left
        self.max_dash = 2
        self.can_dash = self.max_dash
        self.weapon_type = 'katana' # 카타나 또는 대검
        self.STR = 20
        self.critical = 0.05
        self.critical_damage = 1.5

        self.key_state = {'A':False, 'D':False, 'W':False, 'S':False}

        self.idle = Idle(self)
        self.move = Move(self)
        self.attack = Attack(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {A_down : self.move, A_up : self.move, S_down:self.move, S_up:self.move, D_down:self.move, D_up:self.move, W_down:self.move, W_up:self.move},
            self.move: {A_up:self.idle, S_up:self.idle, D_up:self.idle, W_up: self.idle},
            self.attack: {}
        })

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))