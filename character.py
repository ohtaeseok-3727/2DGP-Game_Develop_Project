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
from pico2d import *
import title_mode
import math

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

def stun_end(e):
    return e[0] == 'STUN_END'

PIXEL_PER_METER = (10.0 / 0.5)  # 10 pixel 50 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.02
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


class Stun:
    def __init__(self, character):
        self.character = character
        self.stun_duration = 0.5
        self.stun_timer = 0
        self.knockback_speed = 200
        self.knockback_dir_x = 0
        self.knockback_dir_y = 0

    def enter(self, e):
        self.stun_timer = 0
        self.character.frame = 0

        # 넉백 방향 설정 (e[1]에서 받아옴)
        if len(e) > 1 and isinstance(e[1], tuple):
            self.knockback_dir_x, self.knockback_dir_y = e[1]
        else:
            self.knockback_dir_x = 0
            self.knockback_dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        self.stun_timer += game_framework.frame_time

        if self.stun_timer < 0.2:
            knockback_amount = self.knockback_speed * game_framework.frame_time
            self.character.x += self.knockback_dir_x * knockback_amount
            self.character.y += self.knockback_dir_y * knockback_amount

            try:
                self.character.clamp_to_world()
            except:
                pass

        # 경직 시간 종료
        if self.stun_timer >= self.stun_duration:
            self.character.state_machine.handle_state_event(('STUN_END', 0))

    def draw(self, camera=None):
        sx, sy = camera.apply(self.character.x, self.character.y) if camera else (self.character.x, self.character.y)
        zoom = camera.zoom if camera else 1.0

        # 경직 상태에서는 idle 스프라이트 그리기
        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(0, 76, 18, 19, sx, sy, 18 * zoom, 19 * zoom)
        elif self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(0, 76, 18, 19, 0, 'h', sx, sy, 18 * zoom, 19 * zoom)
        elif self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(0, 76, 18, 19, sx, sy, 18 * zoom, 19 * zoom)
        elif self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(0, 76, 18, 19, 0, 'h', sx, sy, 18 * zoom, 19 * zoom)

class Die:
    def __init__(self, character):
        self.character = character
        self.fps = 10
        self.frame_time = 0
        self.die_effect = load_image('resource/character/player_die_FX_sprite.png')
        self.effect_frame = 0
        self.max_frames = 9
        self.die_time = 0

        # 애니메이션 관련
        self.start_y = 0
        self.float_duration = 0.3  # 떠오르는 시간
        self.fall_duration = 0.3   # 떨어지는 시간
        self.max_height = 10       # 최대 높이
        self.current_offset_y = 0  # 현재 Y 오프셋
        self.die_frame = 0         # 넘어지는 애니메이션 프레임 (0~2)
        self.die_frame_time = 0

    def enter(self, e):
        self.frame_time = get_time()
        self.die_time = get_time()
        self.die_frame_time = get_time()
        self.character.dir = 0
        self.character.updown_dir = 0
        self.effect_frame = 0
        self.character.frame = 0
        self.start_y = self.character.y
        self.current_offset_y = 0
        self.die_frame = 0

    def exit(self, e):
        pass

    def do(self):
        current_time = get_time()
        elapsed_time = current_time - self.die_time

        if current_time - self.frame_time > 1.0 / self.fps:
            if self.effect_frame < self.max_frames - 1:
                self.effect_frame = (self.effect_frame+FRAMES_PER_ACTION*ACTION_PER_TIME*game_framework.frame_time) % 9
            self.frame_time = current_time

        # 떠오르기 -> 떨어지기 애니메이션
        if elapsed_time < self.float_duration:
            # 떠오르는 중
            progress = elapsed_time / self.float_duration
            self.current_offset_y = self.max_height * progress
        elif elapsed_time < self.float_duration + self.fall_duration:
            # 떨어지는 중
            progress = (elapsed_time - self.float_duration) / self.fall_duration
            self.current_offset_y = self.max_height * (1 - progress)

            # 떨어지면서 넘어지는 애니메이션 프레임 업데이트
            if current_time - self.die_frame_time > self.fall_duration / 3:
                if self.die_frame < 2:
                    self.die_frame += 1
                self.die_frame_time = current_time
        else:
            # 떨어진 후
            self.current_offset_y = 0
            self.die_frame = 2

        # 3초 후 타이틀로 이동
        if current_time - self.die_time >= 3.0:
            game_framework.change_mode(title_mode)

    def draw(self, camera=None):
        # 떠오른 만큼 Y 좌표 조정
        adjusted_y = self.character.y + self.current_offset_y
        sx, sy = (camera.apply(self.character.x, adjusted_y)) if camera else (self.character.x, adjusted_y)
        zoom = camera.zoom if camera else 1.0

        elapsed_time = get_time() - self.die_time

        # 떠오르는 동안 idle 스프라이트
        if elapsed_time < self.float_duration:
            if self.character.face_dir == 1:
                self.character.image.clip_draw(
                    int(self.die_frame) * 18, 76,
                    18, 19,
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
            else:
                self.character.image.clip_composite_draw(
                    int(self.die_frame) * 18, 76,
                    18, 19,
                    0, 'h',
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
        # 떨어지는 동안 넘어지는 애니메이션 (y=76, 3프레임)
        elif elapsed_time < self.float_duration + self.fall_duration:
            if self.character.face_dir == 1:
                self.character.image.clip_draw(
                    int(self.die_frame) * 18, 76,
                    18, 19,
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
            else:
                self.character.image.clip_composite_draw(
                    int(self.die_frame) * 18, 76,
                    18, 19,
                    0, 'h',
                    sx, sy,
                    18 * zoom, 19 * zoom
                )

        # 바닥에 떨어진 후 - idle 스프라이트를 90도 회전
        else:
            if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
                self.character.image.clip_composite_draw(
                    0, 57, 18, 19,
                    -1.5708, '',  # -90도 회전
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
            elif self.character.face_dir == -1 and self.character.face_updown_dir == -1:
                self.character.image.clip_composite_draw(
                    0, 57, 18, 19,
                    -1.5708, 'h',  # -90도 회전 + 좌우 반전
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
            elif self.character.face_dir == 1 and self.character.face_updown_dir == 1:
                self.character.image.clip_composite_draw(
                    0, 38, 18, 19,
                    -1.5708, '',
                    sx, sy,
                    18 * zoom, 19 * zoom
                )
            elif self.character.face_dir == -1 and self.character.face_updown_dir == 1:
                self.character.image.clip_composite_draw(
                    0, 38, 18, 19,
                    -1.5708, 'h',
                    sx, sy,
                    18 * zoom, 19 * zoom
                )

        # 사망 이펙트 애니메이션 그리기
        if self.die_effect:
            self.die_effect.clip_draw(
                int(self.effect_frame) * 105, 0,
                105, 105,
                sx, sy,
                105 * zoom, 105 * zoom
            )
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

        self.character.prev_x = self.character.x
        self.character.prev_y = self.character.y

        self.character.x += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time
        self.character.y += self.character.updown_dir * RUN_SPEED_PPS * game_framework.frame_time

        if (not self.character.left_pressed and not self.character.right_pressed and
                not self.character.up_pressed and not self.character.down_pressed):
            self.character.state_machine.handle_state_event(('STOP', 0))

        try:
            self.character.clamp_to_world()
        except Exception:
            pass
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

        self.prev_x = self.x
        self.prev_y = self.y

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
        self.ATK = 1000
        self.critical = 0.00
        self.critical_damage = 1.5

        self.max_hp = 100
        self.now_hp = self.max_hp

        self.hit_cooldown = 0.5
        self.last_hit_time = -self.hit_cooldown

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.idle = Idle(self)
        self.move = Move(self)
        self.die = Die(self)
        self.dash = dashstate(self)
        self.stun = Stun(self)
        self.weapon = weapon(self)
        self.attack = Attack(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {space_down : self.idle, F_down:self.idle, key_down: self.move, lambda e: e[0] == 'STUN': self.stun},
            self.move: {space_down : self.move, F_down:self.idle, key_down: self.move, key_up: self.move, stop: self.idle, lambda e: e[0] == 'STUN': self.stun},
            self.stun: {stun_end: self.idle},
            self.die : {}
        })

        self.inventory = []

        game_world.add_collision_pairs('character:monster', self, None)
        game_world.add_collision_pairs('building:character', None, self)
        game_world.add_collision_pairs('character:Boss', self, None)

    def add_item(self, item):
        self.inventory.append(item)
        item.apply_effect(self)
        print(f'{item.item_type} 획득')

    def update(self, camera=None):
        if self.cursor and self.state_machine.cur_state != self.die:
            dx, dy = self.cursor.x - self.x, self.cursor.y - self.y
            self.face_dir = 1 if dx >= 0 else -1
            self.face_updown_dir = 1 if dy >= 0 else -1

        if self.can_dash < 2 and get_time() - self.dash_recovery_time > 5:
            self.can_dash += 1
            print('대쉬 회복')
            self.dash_recovery_time = get_time()

        if self.now_hp <= 0 and self.state_machine.cur_state != self.die:
            self.state_machine.cur_state = self.die
            self.die.enter(None)
            return

        self.state_machine.update()
        self.attack.update()
        self.dash.update()
        self.weapon.update(camera)

    def get_bb(self):
        return self.x - 4, self.y - 7, self.x + 4, self.y + 4

    def draw(self, camera=None):
        self.state_machine.draw(camera)
        self.attack.draw(camera)

        if self.state_machine.cur_state != self.die:
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
        current_time = get_time()

        if group == 'building:character':
            # 캐릭터와 빌딩의 바운딩 박스 가져오기
            char_left, char_bottom, char_right, char_top = self.get_bb()
            build_left, build_bottom, build_right, build_top = other.get_bb()

            # 겹친 영역 계산
            overlap_x = min(char_right, build_right) - max(char_left, build_left)
            overlap_y = min(char_top, build_top) - max(char_bottom, build_bottom)

            # 더 작은 겹침을 기준으로 밀어내기
            if overlap_x < overlap_y:
                # x축으로 밀어내기
                if self.x < other.x:
                    self.x -= overlap_x
                else:
                    self.x += overlap_x
            else:
                # y축으로 밀어내기
                if self.y < other.y:
                    self.y -= overlap_y
                else:
                    self.y += overlap_y

        elif self.dash.working:
            return

        elif group == 'character:monster':
            if current_time - self.last_hit_time >= self.hit_cooldown:
                self.now_hp = max(0, self.now_hp - other.damage)
                self.last_hit_time = current_time

            # 충돌 시 서로 밀어내기
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                # 정규화된 방향 벡터
                nx = dx / distance
                ny = dy / distance

                # 최소 거리 계산
                char_left, char_bottom, char_right, char_top = self.get_bb()
                char_half_w = (char_right - char_left) / 2
                char_half_h = (char_top - char_bottom) / 2

                monster_half_w = other.frame_width / 2
                monster_half_h = other.frame_height / 2

                min_distance = math.sqrt((char_half_w + monster_half_w) ** 2 +
                                         (char_half_h + monster_half_h) ** 2) * 0.7

                if distance < min_distance:
                    # 겹친 정도 계산
                    overlap = min_distance - distance

                    # 각 객체를 반대 방향으로 밀어냄 (50:50 비율)
                    push_distance = overlap / 2
                    self.x += nx * push_distance
                    self.y += ny * push_distance
                    other.x -= nx * push_distance
                    other.y -= ny * push_distance

                    # 월드 경계 내로 제한
                    try:
                        self.clamp_to_world()
                    except:
                        pass



    def clamp_to_world(self):
        try:
            left, bottom, right, top = self.get_bb()
            half_w = (right - left) / 2.0
            half_h = (top - bottom) / 2.0
        except Exception:
            half_w = getattr(self, 'frame_width', 0) / 2.0
            half_h = getattr(self, 'frame_height', 0) / 2.0

        self.x = max(half_w, min(self.x, WorldMap.width - half_w))
        self.y = max(half_h, min(self.y, WorldMap.height - half_h))




    def handle_event(self, event, camera=None):
        if self.state_machine.cur_state != self.die and self.state_machine.cur_state != self.stun:
            try:
                self.attack.on_input(event, camera)
            except Exception:
                pass
            self.state_machine.handle_state_event(('INPUT', event))
