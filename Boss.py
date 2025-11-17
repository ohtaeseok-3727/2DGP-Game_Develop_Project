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

        if self.monster.target:
            dx = self.monster.target.x - self.monster.x
            dy = self.monster.target.y - self.monster.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0:
                dir_x = dx / distance
                dir_y = dy / distance

                if abs(dx) > abs(dy):
                    self.monster.face_dir = 1 if dx > 0 else -1

                self.monster.x += dir_x * MONSTER_SPEED_PPS * game_framework.frame_time
                self.monster.y += dir_y * MONSTER_SPEED_PPS * game_framework.frame_time

    def draw(self, camera):
        sx, sy = camera.apply(self.monster.x, self.monster.y) if camera else (self.monster.x, self.monster.y)
        zoom = camera.zoom if camera else 1.0

        if self.monster.face_dir == 1:
            self.monster.image.clip_draw(
                int(self.monster.frame) * self.monster.frame_width, self.monster.frame_height,
                self.monster.frame_width, self.monster.frame_height,
                sx, sy,
                self.monster.frame_width * zoom, self.monster.frame_height * zoom
            )
        else:
            self.monster.image.clip_composite_draw(
                int(self.monster.frame) * self.monster.frame_width, self.monster.frame_height,
                self.monster.frame_width, self.monster.frame_height,
                0, 'h',
                sx, sy,
                self.monster.frame_width * zoom, self.monster.frame_height * zoom
            )



class Monster:
    images = {}
    hp_bar = None
    hp_background = None
    def __init__(self, x, y, monster_type='blue_slime'):
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.frame = 0
        self.frame_time = 0
        self.fps = 10
        self.is_alive = True
        self.target = None
        self.face_dir = 1

        if monster_type == 'small_blue_slime':
            self.hp = 50
            self.max_hp = 50
            self.damage = 5
            self.frame_width = 17
            self.frame_height = 12
            self.max_frames = 6
            self.detection_range = 150
            self.speed_multiplier = 1.0
            self.attack_range = 10

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
            self.speed_multiplier = 0.8
            self.attack_range = 10

            if 'blue_slime' not in Monster.images:
                Monster.images['blue_slime'] = load_image('resource/monster/blue_slime_sprite_sheet.png')
            self.image = Monster.images['blue_slime']

        self.hit_cooldown = 0.1

        if Monster.hp_bar == None or Monster.hp_background == None:
            Monster.hp_bar = load_image('resource/character/HP.png')
            Monster.hp_background = load_image('resource/character/HP_Background.png')

        self.monster_type = monster_type
        self.name = monster_type

        self.idle = Idle(self)
        self.move = Move(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {target_in_range: self.move},
            self.move: {target_out_of_range: self.idle}
        })

        game_world.add_collision_pairs('character:monster', None, self)
        game_world.add_collision_pairs('monster:attack', self, None)

    def set_target(self, target):
        self.target = target
        pass
    def update(self, camera=None):
        if not self.is_alive:
            return

        self.state_machine.update()

    def get_bb(self):
        half_w = (self.frame_width / 2) - self.frame_width / 20
        half_h = (self.frame_height / 2) - self.frame_height / 5
        return (
            self.x - half_w,
            self.y - half_h,
            self.x + half_w,
            self.y + half_h
        )

    def take_damage(self, damage):
        """데미지를 받는 메서드"""
        if not self.is_alive:
            return

        self.hp -= damage
        print(f'{self.name}이(가) {damage} 데미지를 받음. 남은 HP: {self.hp}')
        if self.hp <= 0:
            self.die()

    def die(self):
        if not self.is_alive:
            return

        print(f'{self.name}이(가) 사망했습니다.')
        self.is_alive = False

        try:
            game_world.remove_collision_object(self)
            game_world.remove_object(self)
        except Exception as e:
            print(f'몬스터 제거 오류: {e}')

    def handle_collision(self, group, other):
        if group == 'monster:monster':
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx * dx + dy * dy)

            # 최소 거리 계산 (두 몬스터의 반경 합)
            min_distance = (self.frame_width + other.frame_width) / 2

            if distance < min_distance and distance > 0:
                # 겹침 정도 계산
                overlap = min_distance - distance

                # 정규화된 방향 벡터
                nx = dx / distance
                ny = dy / distance

                # 각 몬스터를 반대 방향으로 밀어냄
                push_distance = overlap / 2
                self.x += nx * push_distance
                self.y += ny * push_distance
                other.x -= nx * push_distance
                other.y -= ny * push_distance

        if group == 'monster:attack':
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

        if camera:
            zoom = camera.zoom
            sx, sy = camera.apply(self.x, self.y)
            bar_width = 50 * zoom
            bar_height = 5 * zoom
            bar_x = sx - bar_width / 2
            bar_y = sy + (self.frame_height / 2 + 10) * zoom

            if Monster.hp_background:
                Monster.hp_background.draw(bar_x + 52, bar_y + 11, 104, 22)

            hp_ratio = max(0, min(1, self.hp / self.max_hp))
            hp_width = 100 * hp_ratio

            if self.hp and hp_ratio > 0:
                Monster.hp_bar.clip_draw(
                    0, 0,
                    int(200 * hp_ratio), 30,
                    bar_x + 2 + hp_width / 2, bar_y + 10,
                    hp_width, 20
                )