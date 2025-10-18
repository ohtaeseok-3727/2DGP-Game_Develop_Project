from pico2d import *
from worldmap import *
from sdl2 import *
from state_machine import StateMachine
import math
import ctypes
for sdl2.mouse import SDL_GetMouseState

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

def key_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN
def key_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP

def stop(e):
    return e[0] == 'STOP'

class weapon:
    #기본 카타나
    default_katana = {'name': '기본 카타나', 'damage': 0, 'attack_width' :40, 'attack_height': 88, 'speed': 1.0}
    #무라마사(평타 강화 : 2회 연속 공격)
    katana_muramasa = {'name': '무라마사', 'damage': 0, 'attack_width' :66, 'attack_height': 133, 'speed': 1.2}
    #호우(원거리 평타)
    katana_hou = {'name': '호우', 'damage': 0, 'width' :79, 'attack_height': 79, 'attack_speed': 1.0}
    #기본 대검
    default_greatsword = {'name': '기본 대검', 'damage': 0, 'attack1_width' :70, 'attack1_height': 66, 'attack2_width' :75, 'attack2_height': 74, 'speed': 0.8}
    #쯔바이핸더(평타 강화)
    greatsword_zweihander = {'name': '쯔바이핸더', 'damage': 0, 'attack1_width' :90, 'attack1_height': 82, 'attack2_width' :100, 'attack2_height': 98, 'speed': 1.0}
    #브레이커(특수 기술 생성)
    greatsword_breaker = {'name': '브레이커', 'damage': 0, 'attack1_width' :74, 'attack1_height': 111, 'attack2_width' :120, 'attack2_height': 116, 'speed': 0.9}

    def __init__(self, character):
        self.character = character
        self.x = character.x
        self.y = character.y

        self.angle = 0
        self.waist_x = 0
        self.waist_y = 0

        self.default_katana_image = load_image('resource/weapon/katana/katana_Default.png')
        self.katana_hou_image = load_image('resource/weapon/katana/katana_Default.png')
        self.katana_muramasa_imgae = load_image('resource/weapon/katana/katana_Default.png')
        self.default_greatsword_image = load_image('resource/weapon/greatsword/Greatsword_Default.png')
        self.greatsword_zweihander_image = load_image('resource/weapon/greatsword/Greatsword_Zweihander.png')
        self.greatsword_breaker_image = load_image('resource/weapon/greatsword/Greatsword_Breaker.png')
        pass
    def update(self):
        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        mx = x.value
        my = WorldMap.height - y.value

        # 무기 위치를 캐릭터의 허리 부근으로 설정(캐릭터의 중심보다 살짝 아래)
        self.waist_x = self.character.x
        self.waost_y = self.character.y - 10

        dx = mx - self.waist_x
        dy = my - self.waist_y
        self.angle = math.atan2(dy, dx)
    def do(self):
        pass
    def draw(self):
        self.default_katana_image.clip_draw(0,0,14,40,self.x,self.y, 28, 80)
        pass


class Move:
    def __init__(self, character):
        self.character = character
        self.fps = 15
        self.frame_time = 0
    def enter(self, e):
        self.frame_time = get_time()
        self.update_direction(e)
        pass

    def update_direction(self, e):
        if A_down(e):
            self.character.left_pressed = True
        elif A_up(e):
            self.character.left_pressed = False

        if D_down(e):
            self.character.right_pressed = True
        elif D_up(e):
            self.character.right_pressed = False

        if W_down(e):
            self.character.up_pressed = True
        elif W_up(e):
            self.character.up_pressed = False

        if S_down(e):
            self.character.down_pressed = True
        elif S_up(e):
            self.character.down_pressed = False

        # 현재 눌린 키 상태에 따라 dir 계산
        self.character.dir = 0
        if self.character.right_pressed:
            self.character.dir += 1
        if self.character.left_pressed:
            self.character.dir -= 1

        self.character.updown_dir = 0
        if self.character.up_pressed:
            self.character.updown_dir += 1
        if self.character.down_pressed:
            self.character.updown_dir -= 1


    def exit(self, e):
        pass
    def do(self):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame + 1) % 8
            self.frame_time = get_time()

        self.character.x += self.character.dir * 5
        self.character.y += self.character.updown_dir * 5

        if self.character.dir == 0 and self.character.updown_dir == 0:
            self.character.state_machine.handle_state_event(('STOP', 0))
        pass
    def draw(self):
        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(self.character.frame * 18, 19, 18, 19, self.character.x, self.character.y,
                                           54, 57)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 19, 18, 19, 0, 'h', self.character.x,
                                                     self.character.y, 54, 57)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(self.character.frame * 18, 0, 18, 19, self.character.x, self.character.y,
                                           54, 57)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
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
        self.character.dir = 0
        self.character.updown_dir = 0
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
        self.weapon_rank = 0 # 0: 기본 1: 원거리 참격 2: 근접 참격 강화
        self.STR = 20
        self.critical = 0.05
        self.critical_damage = 1.5

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.idle = Idle(self)
        self.move = Move(self)
        self.attack = Attack(self)
        self.weapon = weapon(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {key_down: self.move},
            self.move: {key_down: self.move, key_up: self.move, stop: self.idle},
            self.attack: {}
        })

    def update(self):
        mx, my = 0, 0
        try:
            x = ctypes.c_int(0)
            y = ctypes.c_int(0)
            SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
            mx = x.value
            my = WorldMap.height - y.value

            dx, dy = mx - self.x, my - self.y
            self.face_dir = 1 if dx >= 0 else -1
            self.face_updown_dir = 1 if dy >= 0 else -1
        except Exception as e:
            pass
        except:
            pass
        self.state_machine.update()
        self.weapon.update()

    def draw(self):
        self.state_machine.draw()
        self.weapon.draw()
    def handle_event(self, event):

        self.state_machine.handle_state_event(('INPUT', event))
