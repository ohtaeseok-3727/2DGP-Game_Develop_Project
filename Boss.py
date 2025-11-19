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
        self.monster.images.clip_draw(
            frame_index * self.monster.frame_width, self.monster.frame_height*2,
            self.monster.frame_width, self.monster.frame_height,
            sx, sy,
            self.monster.width * zoom, self.monster.height * zoom
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

            if distance >= self.monster.detection_range:
                self.monster.state_machine.handle_state_event(('TARGET_OUT', 0))
                return

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
            self.monster.images.clip_draw(
                int(self.monster.frame) * self.monster.frame_width, self.monster.frame_height,
                self.monster.frame_width, self.monster.frame_height,
                sx, sy,
                self.monster.width * zoom, self.monster.height * zoom
            )
        else:
            self.monster.images.clip_composite_draw(
                int(self.monster.frame) * self.monster.frame_width, self.monster.frame_height,
                self.monster.frame_width, self.monster.frame_height,
                0, 'h',
                sx, sy,
                self.monster.width * zoom, self.monster.height * zoom
            )



class KingSlime:
    images = None
    hp_bar = None
    hp_background = None
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = 'KingSlime'
        self.frame = 0
        self.frame_time = 0
        self.fps = 10
        self.is_alive = True
        self.target = None
        self.face_dir = 1
        self.hp = 5000
        self.max_hp = 5000
        self.frame_width = 27
        self.frame_height = 22
        self.max_frames = 10
        self.detection_range = 300
        self.speed_multiplier = 0.8
        self.attack_range = 10
        self.width = 135
        self.height = 110


        self.hit_cooldown = 0.1

        if KingSlime.images == None:
            KingSlime.images = load_image('resource/monster/blue_slime_sprite_sheet.png')

        if KingSlime.hp_bar == None or KingSlime.hp_background == None:
            KingSlime.hp_bar = load_image('resource/character/HP.png')
            KingSlime.hp_background = load_image('resource/character/HP_Background.png')

        self.idle = Idle(self)
        self.move = Move(self)

        self.state_machine = StateMachine(self.idle, {
            self.idle: {target_in_range: self.move},
            self.move: {target_out_of_range: self.idle}
        })

        game_world.add_collision_pairs('character:Boss', None, self)
        game_world.add_collision_pairs('Boss:attack', self, None)
        game_world.add_collision_pairs('Boss:monster', self, None)

    def set_target(self, target):
        self.target = target
        pass
    def update(self, camera=None):
        if not self.is_alive:
            return

        self.state_machine.update()

    def get_bb(self):
        half_w = (self.width / 2) - self.width / 20
        half_h = (self.height / 2) - self.height / 5
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
            pass

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

        screen_w = get_canvas_width()
        screen_h = get_canvas_height()

        total_bar_width = 1000
        total_bar_height = 40
        margin_bottom = 20

        center_x = screen_w / 2
        bar_x_center = center_x
        bar_y = margin_bottom + total_bar_height / 2

        if KingSlime.hp_background:
            KingSlime.hp_background.draw(bar_x_center, bar_y, total_bar_width + 4, total_bar_height)

        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        hp_display_width = total_bar_width * hp_ratio

        if hp_ratio > 0 and KingSlime.hp_bar:
            src_w = getattr(KingSlime.hp_bar, 'w', None)
            src_h = getattr(KingSlime.hp_bar, 'h', None)
            if src_w and src_h:
                clip_w = max(1, int(src_w * hp_ratio))
                clip_draw_x = bar_x_center - total_bar_width / 2 + hp_display_width / 2
                KingSlime.hp_bar.clip_draw(0, 0, clip_w, src_h, clip_draw_x, bar_y, hp_display_width,
                                           total_bar_height - 2)
            else:
                KingSlime.hp_bar.draw(bar_x_center - (total_bar_width - hp_display_width) / 2, bar_y, hp_display_width,
                                      total_bar_height - 2)