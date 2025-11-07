from pico2d import *
import math
import game_framework
import game_world
from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.3)
MONSTER_SPEED_KMPH = 10.0
MONSTER_SPEED_MPM = (MONSTER_SPEED_KMPH * 1000.0 / 60.0)
MONSTER_SPEED_MPS = (MONSTER_SPEED_MPM / 60.0)
MONSTER_SPEED_PPS = (MONSTER_SPEED_MPS * PIXEL_PER_METER)

def target_in_range(e):
    return e[0] == 'TARGET_IN_RANGE'

def target_out_of_range(e):
    return e[0] == 'TARGET_OUT'

class Idle:
    def __init__(self, monster):
        self.monster = monster

    def enter(self, e):
        self.monster.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.monster.frame = (self.monster.frame + MONSTER_SPEED_PPS / self.monster.frame_width * game_framework.frame_time) % 6

        # 타겟 감지
        if self.monster.target:
            dx = self.monster.target.x - self.monster.x
            dy = self.monster.target.y - self.monster.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < self.monster.detection_range:
                self.monster.state_machine.handle_state_event(('TARGET_IN_RANGE', 0))

    def draw(self, camera):
        zoom = camera.zoom if camera else 1.0
        sx, sy = camera.apply(self.monster.x, self.monster.y) if camera else (self.monster.x, self.monster.y)

        frame_index = int(self.monster.frame)
        self.monster.image.clip_draw(
            frame_index * self.monster.frame_width, self.monster.frame_height*2,
            self.monster.frame_width, self.monster.frame_height,
            sx, sy,
            self.monster.frame_width * zoom, self.monster.frame_height * zoom
        )

class Move:
    def __init__(self, monster):
        self.monster = monster

    def enter(self, e):
        self.monster.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.monster.frame = (self.monster.frame + MONSTER_SPEED_PPS / self.monster.frame_width * game_framework.frame_time) % 5

        if self.monster.target and (self.monster.target.is_alive if hasattr(self.monster.target, 'is_alive') else True):
            dx = self.monster.target.x - self.monster.x
            dy = self.monster.target.y - self.monster.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance >= self.monster.detection_range or distance <= self.monster.attack_range:
                self.monster.state_machine.handle_state_event(('TARGET_OUT', 0))
            elif distance > self.monster.attack_range:
                nx = dx / distance
                ny = dy / distance

                move_speed = MONSTER_SPEED_PPS * self.monster.speed_multiplier * game_framework.frame_time
                self.monster.x += nx * move_speed
                self.monster.y += ny * move_speed

    def draw(self, camera):
        zoom = camera.zoom if camera else 1.0
        sx, sy = camera.apply(self.monster.x, self.monster.y) if camera else (self.monster.x, self.monster.y)

        self.monster.image.clip_draw(
            int(self.monster.frame) * self.monster.frame_width, self.monster.frame_height,
            self.monster.frame_width, self.monster.frame_height,
            sx, sy,
            self.monster.frame_width * zoom, self.monster.frame_height * zoom
        )



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
            self.frame_width = 27
            self.frame_height = 22
            self.max_frames = 10
            self.detection_range = 200
            self.attack_range = 30
            self.speed_multiplier = 0.8

            if 'blue_slime' not in Monster.images:
                Monster.images['blue_slime'] = load_image('resource/monster/blue_slime_sprite_sheet.png')
            self.image = Monster.images['blue_slime']

        self.hit_cooldown = 0

        self.idle = Idle(self)
        self.move = Move(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {target_in_range: self.move},
            self.move: {target_out_of_range: self.idle}
        })

    def set_target(self, target):
        self.target = target
        pass
    def update(self, camera=None):
        if not self.is_alive:
            return

        self.state_machine.update()

    def take_damage(self, damage):
         pass

    def die(self):

         pass

    def get_bb(self):
        half_w = (self.frame_width / 2) - self.frame_width / 20
        half_h = (self.frame_height / 2) - self.frame_height / 5
        return (
            self.x - half_w,
            self.y - half_h,
            self.x + half_w,
            self.y + half_h
        )

    def handle_collision(self, group, other):
        pass

    def draw(self, camera=None):
        if not self.is_alive:
            return

        self.state_machine.draw(camera)
        # 바운딩 박스 그리기
        left, bottom, right, top = self.get_bb()
        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            draw_rectangle(sl, sb, sr, st)
        else:
            draw_rectangle(left, bottom, right, top)

        # HP 바 그리기(임시)
        if camera:
            zoom = camera.zoom
            sx, sy = camera.apply(self.x, self.y)
            bar_width = 40 * zoom
            bar_height = 5 * zoom
            bar_x = sx - bar_width / 2
            bar_y = sy + (self.frame_height / 2 + 10) * zoom

            # HP 바 테두리
            draw_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height)

            # HP 바 내부
            hp_ratio = max(0, self.hp / self.max_hp)
            if hp_ratio > 0:
                draw_rectangle(bar_x, bar_y, bar_x + bar_width * hp_ratio, bar_y + bar_height)