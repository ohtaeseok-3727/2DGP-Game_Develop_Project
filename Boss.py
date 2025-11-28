from pico2d import *
import math
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
from worldmap import WorldMap

PIXEL_PER_METER = (10.0 / 0.3)
MONSTER_SPEED_KMPH = 10.0
MONSTER_SPEED_MPM = (MONSTER_SPEED_KMPH * 1000.0 / 60.0)
MONSTER_SPEED_MPS = (MONSTER_SPEED_MPM / 60.0)
MONSTER_SPEED_PPS = (MONSTER_SPEED_MPS * PIXEL_PER_METER)

class KingSlime:
    images = None
    hp_bar = None
    hp_background = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = 'KingSlime'
        self.frame = 0
        self.is_alive = True
        self.target = None
        self.face_dir = 1
        self.hp = 5000
        self.max_hp = 5000
        self.frame_width = 27
        self.frame_height = 22
        self.detection_range = 300
        self.attack_range = 50
        self.width = 135
        self.height = 110
        self.hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        self.state = 'Idle'

        self.tx, self.ty = x, y

        if KingSlime.images == None:
            KingSlime.images = load_image('resource/monster/blue_slime_sprite_sheet.png')
        if KingSlime.hp_bar == None or KingSlime.hp_background == None:
            KingSlime.hp_bar = load_image('resource/character/HP.png')
            KingSlime.hp_background = load_image('resource/character/HP_Background.png')

        self.build_behavior_tree()

        game_world.add_collision_pairs('character:Boss', None, self)
        game_world.add_collision_pairs('Boss:attack', self, None)
        game_world.add_collision_pairs('Boss:monster', self, None)

    def set_target(self, target):
        self.target = target

    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2

    def move_little_to(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            self.face_dir = 1 if dx > 0 else -1
            move_distance = MONSTER_SPEED_PPS * game_framework.frame_time
            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance

            half_w = (self.width / 2) * max(0.4, self.hp_ratio)
            half_h = (self.height / 2) * max(0.4, self.hp_ratio)
            self.x = max(half_w, min(self.x, WorldMap.width - half_w))
            self.y = max(half_h, min(self.y, WorldMap.height - half_h))

    def target_exists(self):
        if self.target and hasattr(self.target, 'now_hp') and self.target.now_hp > 0:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def target_nearby(self, range):
        if self.target and hasattr(self.target, 'now_hp') and self.target.now_hp > 0:
            if self.distance_less_than(self.target.x, self.target.y, self.x, self.y, range):
                return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def in_attack_range(self):
        if not self.target or not hasattr(self.target, 'now_hp') or self.target.now_hp <= 0:
            return BehaviorTree.FAIL

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= self.attack_range:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def low_hp(self):
        if self.hp_ratio < 0.3:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def move_to_target(self):
        if not self.target or not hasattr(self.target, 'now_hp') or self.target.now_hp <= 0:
            return BehaviorTree.FAIL

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance

            self.x += dir_x * MONSTER_SPEED_PPS * game_framework.frame_time
            self.y += dir_y * MONSTER_SPEED_PPS * game_framework.frame_time

            self.face_dir = 1 if dx > 0 else -1
            self.state = 'Move'
            return BehaviorTree.RUNNING

        return BehaviorTree.SUCCESS

    def attack_target(self):
        self.state = 'Idle'
        # 공격 로직 추가 예정
        return BehaviorTree.SUCCESS


    def idle_state(self):
        self.state = 'Idle'
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        c_target_exists = Condition('타겟 존재?', self.target_exists)
        c_target_nearby = Condition('타겟이 근처에?', self.target_nearby, self.detection_range / PIXEL_PER_METER)
        c_in_attack_range = Condition('공격 범위 안?', self.in_attack_range)
        c_low_hp = Condition('체력 부족?', self.low_hp)

        a_move_to_target = Action('타겟으로 이동', self.move_to_target)
        a_attack = Action('공격', self.attack_target)
        a_idle = Action('대기', self.idle_state)

        attack_sequence = Sequence('공격 시퀀스', c_in_attack_range, a_attack)
        chase_sequence = Sequence('추격 시퀀스', c_target_nearby, a_move_to_target)

        root = Selector('보스 AI',
            attack_sequence,
            chase_sequence,
            a_idle
        )

        self.bt = BehaviorTree(root)

    def update(self, camera=None):
        if not self.is_alive:
            return

        if self.state == 'Move':
            self.frame = (self.frame + MONSTER_SPEED_PPS / self.frame_width * game_framework.frame_time) % 5
        else:
            self.frame = (self.frame + MONSTER_SPEED_PPS / self.frame_width * game_framework.frame_time) % 6

        self.bt.run()
        self.hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))

    def get_bb(self):
        half_w = (self.width / 2) - self.width / 20
        half_h = (self.height / 2) - self.height / 5
        return (
            self.x - (half_w * max(0.4, self.hp_ratio)),
            self.y - (half_h * max(0.4, self.hp_ratio)),
            self.x + (half_w * max(0.4, self.hp_ratio)),
            self.y + (half_h * max(0.4, self.hp_ratio))
        )

    def take_damage(self, damage):
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
        pass

    def draw(self, camera=None):
        if not self.is_alive:
            return

        sx, sy = camera.apply(self.x, self.y) if camera else (self.x, self.y)
        zoom = camera.zoom if camera else 1.0

        frame_y = self.frame_height * 2 if self.state == 'Idle' else self.frame_height

        if self.face_dir == 1:
            KingSlime.images.clip_draw(
                int(self.frame) * self.frame_width, frame_y,
                self.frame_width, self.frame_height,
                sx, sy,
                self.width * zoom * max(0.4, self.hp_ratio),
                self.height * zoom * max(0.4, self.hp_ratio)
            )
        else:
            KingSlime.images.clip_composite_draw(
                int(self.frame) * self.frame_width, frame_y,
                self.frame_width, self.frame_height,
                0, 'h',
                sx, sy,
                self.width * zoom * max(0.4, self.hp_ratio),
                self.height * zoom * max(0.4, self.hp_ratio)
            )

        left, bottom, right, top = self.get_bb()
        if camera:
            sl, sb = camera.apply(left, bottom)
            sr, st = camera.apply(right, top)
            draw_rectangle(sl, sb, sr, st)

        screen_w = get_canvas_width()
        total_bar_width = 1000
        total_bar_height = 40
        margin_bottom = 20
        bar_x_center = screen_w / 2
        bar_y = margin_bottom + total_bar_height / 2

        if KingSlime.hp_background:
            KingSlime.hp_background.draw(bar_x_center, bar_y, total_bar_width + 4, total_bar_height)

        hp_display_width = total_bar_width * self.hp_ratio
        if self.hp_ratio > 0 and KingSlime.hp_bar:
            clip_draw_x = bar_x_center - total_bar_width / 2 + hp_display_width / 2
            KingSlime.hp_bar.clip_draw(0, 0, int(KingSlime.hp_bar.w * self.hp_ratio), KingSlime.hp_bar.h,
                                       clip_draw_x, bar_y, hp_display_width, total_bar_height - 2)
