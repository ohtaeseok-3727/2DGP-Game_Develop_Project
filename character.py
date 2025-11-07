from Attack import Attack
from dash import dashstate
from weapon import weapon
from worldmap import *
from sdl2 import *
from state_machine import StateMachine
import ctypes
from sdl2.mouse import SDL_GetMouseState
import game_framework

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
            self.character.frame = (self.character.frame + 1) % 8
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
            self.character.image.clip_draw(self.character.frame * 18, 19,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 19,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(self.character.frame * 18, 0,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 0,
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
            self.character.frame = (self.character.frame + 1) % 6
            self.frame_time = get_time()
        pass
    def draw(self, camera=None):
        sx, sy = (camera.apply(self.character.x, self.character.y)) if camera else (self.character.x, self.character.y)
        zoom = camera.zoom if camera else 1.0

        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(self.character.frame*18, 57,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame*18, 57,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(self.character.frame*18, 38,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(self.character.frame*18, 38,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        pass


class character:
    def __init__(self):
        self.image = load_image('resource/character/character_sprites_vertical_merged.png')
        self.cursor = load_image('resource/character/Cursor.png')
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
        self.STR = 20
        self.critical = 0.05
        self.critical_damage = 1.5

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.idle = Idle(self)
        self.move = Move(self)
        self.dash = dashstate(self)
        self.attack = Attack(self)
        self.weapon = weapon(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {space_down : self.idle, F_down:self.idle, key_down: self.move},
            self.move: {space_down : self.move, F_down:self.idle, key_down: self.move, key_up: self.move, stop: self.idle},
        })

    def update(self, camera=None):
        mx, my = 0, 0
        try:
            x = ctypes.c_int(0)
            y = ctypes.c_int(0)
            SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

            screen_x = x.value
            screen_y = WorldMap.height - y.value

            # 카메라가 있으면 스크린 좌표를 월드 좌표로 변환
            if camera:
                mx, my = camera.screen_to_world(screen_x, screen_y)
            else:
                mx, my = screen_x, screen_y

            dx, dy = mx - self.x, my - self.y
            self.face_dir = 1 if dx >= 0 else -1
            self.face_updown_dir = 1 if dy >= 0 else -1

        except Exception as e:
            pass
        except:
            pass

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
        import ctypes
        from sdl2.mouse import SDL_GetMouseState

        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        screen_x = x.value
        screen_y = WorldMap.height - y.value

        if camera:
            world_x, world_y = camera.screen_to_world(screen_x, screen_y)
            sx, sy = camera.apply(world_x, world_y)
        else:
            sx, sy = screen_x, screen_y

        self.cursor.draw(sx, sy, 56, 66)

        left, bottom, right, top = self.get_bb()
        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            draw_rectangle(sl, sb, sr, st)
        else:
            draw_rectangle(left, bottom, right, top)
    def handle_event(self, event, camera=None):
        try:
            self.attack.on_input(event, camera)
        except Exception:
            pass
        self.state_machine.handle_state_event(('INPUT', event))
