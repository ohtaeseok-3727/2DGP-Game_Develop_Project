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
        self.target = target
        pass
    def update(self, camera=None):
        if not self.is_alive:
            return

        self.frame = (self.frame + self.fps * game_framework.frame_time) % self.max_frames

        if self.target and (self.target.is_alive if hasattr(self.target, 'is_alive') else True):
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < self.detection_range and distance > self.attack_range:
                if distance > 0:
                    # 정규화된 방향 벡터
                    nx = dx / distance
                    ny = dy / distance

                    # 시간 기반 이동
                    move_speed = MONSTER_SPEED_PPS * self.speed_multiplier
                    self.x += nx * move_speed * game_framework.frame_time
                    self.y += ny * move_speed * game_framework.frame_time

        # 피격 쿨타임
        if self.hit_cooldown > 0:
            self.hit_cooldown -= game_framework.frame_time

    def take_damage(self, damage):
         pass

    def die(self):
         pass

    def get_bb(self):
         pass

    def handle_collision(self, group, other):
         pass

    def draw(self, camera=None):
        if not self.is_alive:
            return

        zoom = camera.zoom if camera else 1.0
        sx, sy = camera.apply(self.x, self.y) if camera else (self.x, self.y)

        self.image.clip_draw(
            self.frame * self.frame_width, 0,
            self.frame_width, self.frame_height,
            sx, sy,
            self.frame_width * zoom, self.frame_height * zoom
        )

        # HP 바
        if camera:
            bar_width = 40 * zoom
            bar_height = 5 * zoom
            bar_x = sx - bar_width / 2
            bar_y = sy + (self.frame_height / 2 + 10) * zoom

            # 배경 (빨간색)
            draw_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height)

            # HP (초록색)
            hp_ratio = max(0, self.hp / self.max_hp)
            if hp_ratio > 0:
                draw_rectangle(bar_x, bar_y, bar_x + bar_width * hp_ratio, bar_y + bar_height)
