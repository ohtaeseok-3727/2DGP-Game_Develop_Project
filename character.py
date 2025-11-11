from Attack import Attack
from dash import dashstate
from weapon import weapon
from worldmap import *
from sdl2 import *
from state_machine import StateMachine
import ctypes
from sdl2.mouse import SDL_GetMouseState
import game_framework
from cursor import Cursor
import game_world

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

def F_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_f

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def mouse_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_MOUSEBUTTONDOWN and e[1].button == SDL_BUTTON_LEFT
def mouse_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_MOUSEBUTTONUP and e[1].button == SDL_BUTTON_LEFT

def key_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN
def key_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP



def stop(e):
    return e[0] == 'STOP'

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.02
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

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
        try:
            if space_down(e):
                self.character.dash.start()

        except Exception:
            pass
    def do(self):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame+FRAMES_PER_ACTION*ACTION_PER_TIME*game_framework.frame_time) % 8
            self.frame_time = get_time()

        self.character.x += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time
        self.character.y += self.character.updown_dir * RUN_SPEED_PPS * game_framework.frame_time

        if (not self.character.left_pressed and not self.character.right_pressed and
                not self.character.up_pressed and not self.character.down_pressed):
            self.character.state_machine.handle_state_event(('STOP', 0))
        pass
    def draw(self, camera=None):
        sx, sy = (camera.apply(self.character.x, self.character.y)) if camera else (self.character.x, self.character.y)
        zoom = camera.zoom if camera else 1.0

        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(int(self.character.frame) * 18, 19,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(int(self.character.frame) * 18, 19,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(int(self.character.frame) * 18, 0,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(int(self.character.frame) * 18, 0,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
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
        try:
            if space_down(e):
                self.character.dash.start()

        except Exception:
            pass
    def do(self):
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame+FRAMES_PER_ACTION*ACTION_PER_TIME*game_framework.frame_time) % 6
            self.frame_time = get_time()
        pass
    def draw(self, camera=None):
        sx, sy = (camera.apply(self.character.x, self.character.y)) if camera else (self.character.x, self.character.y)
        zoom = camera.zoom if camera else 1.0

        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(int(self.character.frame)*18, 57,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(int(self.character.frame)*18, 57,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(int(self.character.frame)*18, 38,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(int(self.character.frame)*18, 38,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        pass


class character:
    def __init__(self):
        self.image = load_image('resource/character/character_sprites_vertical_merged.png')
        self.cursor = None
        self.hp_background = load_image('resource/character/HP_Background.png')
        self.hp = load_image('resource/character/HP.png')
        self.dash_background = load_image('resource/character/DashHUD.png')
        self.dash_icon = load_image('resource/character/DashHUD 1.png')

        self.x = WorldMap.width/2
        self.y = WorldMap.height/2
        self.frame = 0
        self.updown_dir = 0 # 1: up, -1: down
        self.face_updown_dir = -1 # 1: up, -1: down
        self.face_dir = -1 # 1: right, -1: left
        self.dir = 0 # 1: right, -1: left
        self.max_dash = 2
        self.can_dash = self.max_dash
        self.dash_recovery_time = 0
        self.weapon_type = 'katana' # 카타나 또는 대검
        self.weapon_rank = 0 # 0: 기본 1: 원거리 참격 2: 근접 참격 강화
        self.ATK = 20
        self.critical = 0.00
        self.critical_damage = 1.5

        self.max_hp = 100
        self.now_hp = 60

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.idle = Idle(self)
        self.move = Move(self)
        self.dash = dashstate(self)
        self.weapon = weapon(self)
        self.attack = Attack(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {space_down : self.idle, F_down:self.idle, key_down: self.move},
            self.move: {space_down : self.move, F_down:self.idle, key_down: self.move, key_up: self.move, stop: self.idle},
        })

        game_world.add_collision_pairs('character:monster', self, None)

    def update(self, camera=None):
        if self.cursor:
            dx, dy = self.cursor.x - self.x, self.cursor.y - self.y
            self.face_dir = 1 if dx >= 0 else -1
            self.face_updown_dir = 1 if dy >= 0 else -1

        if self.can_dash < 2 and get_time() - self.dash_recovery_time > 5:
            self.can_dash += 1
            print('대쉬 회복')
            self.dash_recovery_time = get_time()

        self.state_machine.update()
        self.attack.update()
        self.dash.update()
        self.weapon.update(camera)

    def get_bb(self):
        return self.x - 7, self.y - 7, self.x + 7, self.y + 7

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        self.attack.draw(camera)
        self.weapon.draw(camera)

        left, bottom, right, top = self.get_bb()
        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            draw_rectangle(sl, sb, sr, st)
        else:
            draw_rectangle(left, bottom, right, top)

        screen_height = get_canvas_height()
        hp_bar_x = 20
        hp_bar_y = screen_height - 50

        if self.hp_background:
            self.hp_background.draw(hp_bar_x + 105, hp_bar_y + 17, 210, 34)

        hp_ratio = max(0, min(1, self.now_hp / self.max_hp))
        hp_width = 200 * hp_ratio

        # HP 바 이미지 그리기
        if self.hp and hp_ratio > 0:
            self.hp.clip_draw(
                0, 0,
                int(200 * hp_ratio), 30,
                hp_bar_x + 5 + hp_width / 2, hp_bar_y + 17,
                hp_width, 30
            )


        # 대쉬 HUD 그리기
        dash_hud_y = hp_bar_y - 50
        dash_spacing = 40
        dash_size = 30

        for i in range(self.max_dash):
            dash_x = hp_bar_x + i * dash_spacing

            if self.dash_background:
                self.dash_background.draw(dash_x + dash_size / 2, dash_hud_y, dash_size, dash_size)

            if i < self.can_dash and self.dash_icon:
                self.dash_icon.draw(dash_x + dash_size / 2, dash_hud_y, dash_size, dash_size)

    def handle_collision(self, group, other):
        pass



    def handle_event(self, event, camera=None):
        try:
            self.attack.on_input(event, camera)
        except Exception:
            pass
        self.state_machine.handle_state_event(('INPUT', event))
