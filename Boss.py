from pico2d import *
import math
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
from worldmap import WorldMap
import time
import monster
import random

PIXEL_PER_METER = (10.0 / 0.3)
MONSTER_SPEED_KMPH = 10.0
MONSTER_SPEED_MPM = (MONSTER_SPEED_KMPH * 1000.0 / 60.0)
MONSTER_SPEED_MPS = (MONSTER_SPEED_MPM / 60.0)
MONSTER_SPEED_PPS = (MONSTER_SPEED_MPS * PIXEL_PER_METER)

CHARGE_TIME = 1.5
DASH_DISTANCE = 400
DASH_SPEED = 500
DASH_COOLDOWN = 5.0


class BossCutscene:
    """보스 등장 컷신 - 중앙 슬라임이 다른 슬라임들을 흡수하며 성장"""

    def __init__(self, boss_x, boss_y, on_complete):
        self.boss_x = boss_x
        self.boss_y = boss_y
        self.on_complete = on_complete
        self.phase = 'spawn'
        self.timer = 0
        self.is_active = True

        # 중앙 슬라임 (일반 슬라임)
        self.center_slime = {
            'x': boss_x,
            'y': boss_y,
            'size': 1.0,
            'frame': 0,
            'type': 'normal'  # 일반 슬라임
        }

        # 주변 슬라임들 (일반/작은 슬라임 섞여있음)
        self.outer_slimes = []
        self.total_slimes = 15
        self.absorbed_count = 0

        for i in range(self.total_slimes):
            angle = (360 / self.total_slimes) * i
            distance = 250
            x = boss_x + math.cos(math.radians(angle)) * distance
            y = boss_y + math.sin(math.radians(angle)) * distance

            # 홀수는 작은 슬라임, 짝수는 일반 슬라임
            slime_type = 'small' if i % 2 == 0 else 'normal'

            self.outer_slimes.append({
                'x': x,
                'y': y,
                'target_x': boss_x,
                'target_y': boss_y,
                'angle': angle,
                'frame': 0,
                'is_moving': False,
                'is_absorbed': False,
                'move_delay': i * 0.15,
                'type': slime_type
            })

        # 이미지 로드
        self.small_slime_image = load_image('resource/monster/small_blue_slime_sprite_sheet.png')
        self.normal_slime_image = load_image('resource/monster/blue_slime_sprite_sheet.png')
        self.boss_alpha = 0.0
        self.camera_lock_target = (boss_x, boss_y)

    def update(self):
        if not self.is_active:
            return

        self.timer += game_framework.frame_time

        if self.phase == 'spawn':
            self.center_slime['frame'] = (self.center_slime['frame'] + 10 * game_framework.frame_time) % 6

            for slime in self.outer_slimes:
                slime['frame'] = (slime['frame'] + 10 * game_framework.frame_time) % 6

            if self.timer >= 0.5:
                self.phase = 'absorb'
                self.timer = 0

        elif self.phase == 'absorb':
            self.center_slime['frame'] = (self.center_slime['frame'] + 10 * game_framework.frame_time) % 6

            rush_speed = 300
            absorption_distance = 20

            for slime in self.outer_slimes:
                if slime['is_absorbed']:
                    continue

                if self.timer >= slime['move_delay'] and not slime['is_moving']:
                    slime['is_moving'] = True

                if slime['is_moving']:
                    dx = slime['target_x'] - slime['x']
                    dy = slime['target_y'] - slime['y']
                    distance = math.sqrt(dx * dx + dy * dy)

                    if distance > absorption_distance:
                        slime['x'] += (dx / distance) * rush_speed * game_framework.frame_time
                        slime['y'] += (dy / distance) * rush_speed * game_framework.frame_time
                        slime['frame'] = (slime['frame'] + 10 * game_framework.frame_time) % 6
                    else:
                        slime['is_absorbed'] = True
                        self.absorbed_count += 1
                        # 작은 슬라임은 0.3, 일반 슬라임은 0.5 크기 증가
                        size_increase = 0.3 if slime['type'] == 'small' else 0.5
                        self.center_slime['size'] += size_increase

            if self.absorbed_count >= self.total_slimes:
                self.phase = 'transform'
                self.timer = 0

        elif self.phase == 'transform':
            fade_progress = min(1.0, self.timer / 1.0)
            self.center_slime['frame'] = (self.center_slime['frame'] + 10 * game_framework.frame_time) % 6
            self.boss_alpha = fade_progress

            if self.timer >= 1.0:
                self.phase = 'complete'
                self.is_active = False
                if self.on_complete:
                    self.on_complete()

    def get_camera_target(self):
        return self.camera_lock_target

    def draw(self, camera):
        if not self.is_active and self.phase == 'complete':
            return

        zoom = camera.zoom if camera else 1.0

        # 주변 슬라임들 그리기
        for slime in self.outer_slimes:
            if not slime['is_absorbed']:
                sx, sy = camera.apply(slime['x'], slime['y']) if camera else (slime['x'], slime['y'])

                if slime['type'] == 'small':
                    # 작은 슬라임
                    self.small_slime_image.clip_draw(
                        int(slime['frame']) * 17, 24,
                        17, 12,
                        sx, sy,
                        17 * zoom, 12 * zoom
                    )
                else:
                    # 일반 슬라임
                    self.normal_slime_image.clip_draw(
                        int(slime['frame']) * 27, 44,
                        27, 22,
                        sx, sy,
                        27 * zoom, 22 * zoom
                    )

        # 중앙 슬라임 그리기
        if self.phase in ('spawn', 'absorb'):
            sx, sy = camera.apply(self.center_slime['x'], self.center_slime['y']) if camera else (
                self.center_slime['x'], self.center_slime['y'])

            size = self.center_slime['size']
            # 일반 슬라임으로 그리기
            self.normal_slime_image.clip_draw(
                int(self.center_slime['frame']) * 27, 44,
                27, 22,
                sx, sy,
                27 * zoom * size, 22 * zoom * size
            )
        elif self.phase == 'transform':
            sx, sy = camera.apply(self.center_slime['x'], self.center_slime['y']) if camera else (
                self.center_slime['x'], self.center_slime['y'])

            frame_width = 27
            frame_height = 22
            boss_width = 135
            boss_height = 110

            self.normal_slime_image.clip_draw(
                0, frame_height * 2,
                frame_width, frame_height,
                sx, sy,
                boss_width * zoom,
                boss_height * zoom
            )


class KingSlime:
    images = None
    hp_bar = None
    hp_background = None
    hit_effect_image = None
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
        self.attack_range = 200
        self.width = 135
        self.height = 110
        self.hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        self.damage = 15
        self.dash_damage = 30
        self.state = 'Idle'

        self.is_charging = False
        self.is_dashing = False
        self.charge_start_time = 0
        self.dash_target_x = 0
        self.dash_target_y = 0
        self.dash_start_x = 0
        self.dash_start_y = 0
        self.last_dash_time = -DASH_COOLDOWN

        self.hit_characters_during_dash = set()

        self.has_summoned = False

        self.is_hit = False
        self.hit_effect_frame = 0
        self.hit_effect_duration = 0
        self.hit_effect_max_frames = 6
        self.hit_angle = 0

        self.tx, self.ty = x, y

        if KingSlime.images == None:
            KingSlime.images = load_image('resource/monster/blue_slime_sprite_sheet.png')
        if KingSlime.hp_bar == None or KingSlime.hp_background == None:
            KingSlime.hp_bar = load_image('resource/character/HP.png')
            KingSlime.hp_background = load_image('resource/character/HP_Background.png')

        if KingSlime.hit_effect_image == None:
            KingSlime.hit_effect_image = load_image('resource/monster/monster_hit_sprite_sheet.png')

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

    def can_dash(self):
        current_time = time.time()
        if not self.is_charging and not self.is_dashing:
            if current_time - self.last_dash_time >= DASH_COOLDOWN:
                if self.target:
                    dx = self.target.x - self.x
                    dy = self.target.y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance <= self.attack_range:
                        return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def should_summon(self):
        if not self.has_summoned and self.hp_ratio <= 0.5:
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    def charge_and_dash(self):
        current_time = time.time()

        # 이미 차지나 돌진 중이면 계속 실행
        if self.is_charging or self.is_dashing:
            # 차지 중
            if self.is_charging:
                if current_time - self.charge_start_time >= CHARGE_TIME:
                    self.is_charging = False
                    self.is_dashing = True

                    self.hit_characters_during_dash.clear()

                    self.dash_start_x = self.x
                    self.dash_start_y = self.y

                    dx = self.target.x - self.x
                    dy = self.target.y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)

                    if distance > 0:
                        self.dash_target_x = self.x + (dx / distance) * DASH_DISTANCE
                        self.dash_target_y = self.y + (dy / distance) * DASH_DISTANCE
                        self.face_dir = 1 if dx > 0 else -1

                    self.state = 'Dash'
                    print(f"{self.name} 돌진!")
                return BehaviorTree.RUNNING

            # 돌진 중
            if self.is_dashing:
                dx = self.dash_target_x - self.x
                dy = self.dash_target_y - self.y
                distance = math.sqrt(dx * dx + dy * dy)

                half_w = (self.width / 2) * max(0.4, self.hp_ratio)
                half_h = (self.height / 2) * max(0.4, self.hp_ratio)

                if distance < 5 or self.x <= half_w or self.x >= WorldMap.width - half_w or \
                        self.y <= half_h or self.y >= WorldMap.height - half_h:
                    self.is_dashing = False
                    self.last_dash_time = current_time
                    self.state = 'Idle'
                    print(f"{self.name} 돌진 종료!")
                    return BehaviorTree.SUCCESS

                if distance > 0:
                    move_distance = DASH_SPEED * game_framework.frame_time
                    self.x += (dx / distance) * move_distance
                    self.y += (dy / distance) * move_distance

                    self.x = max(half_w, min(self.x, WorldMap.width - half_w))
                    self.y = max(half_h, min(self.y, WorldMap.height - half_h))

                return BehaviorTree.RUNNING

        # 새로운 돌진 시작 조건 체크
        if current_time - self.last_dash_time >= DASH_COOLDOWN:
            if self.target:
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                distance = math.sqrt(dx * dx + dy * dy)

                # 공격 범위 내에 있으면 차지 시작
                if distance <= self.attack_range:
                    self.is_charging = True
                    self.charge_start_time = current_time
                    self.state = 'Charge'
                    print(f"{self.name} 차지 시작! (거리: {distance:.1f})")
                    return BehaviorTree.RUNNING

        # 조건을 만족하지 않으면 FAIL 반환
        return BehaviorTree.FAIL

    def summon_slimes(self):
        if self.has_summoned:
            return BehaviorTree.SUCCESS

        print(f"{self.name} 슬라임 소환!")
        self.has_summoned = True

        for i in range(15):
            angle = (360 / 15) * i
            spawn_x = self.x + math.cos(math.radians(angle)) * 100
            spawn_y = self.y + math.sin(math.radians(angle)) * 100

            if i % 2 == 0:
                slime = monster.Monster(spawn_x, spawn_y, 'small_blue_slime', 1)
            else:
                slime = monster.Monster(spawn_x, spawn_y, 'blue_slime', 1)

            slime.set_target(self.target)
            game_world.add_object(slime, 2)

        return BehaviorTree.SUCCESS

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

    def idle_state(self):
        self.state = 'Idle'
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        c_target_exists = Condition('타겟 존재?', self.target_exists)
        c_target_nearby = Condition('타겟이 근처에?', self.target_nearby, self.detection_range)
        c_should_summon = Condition('소환 조건?', self.should_summon)

        a_summon = Action('슬라임 소환', self.summon_slimes)
        a_charge_and_dash = Action('차지 및 돌진', self.charge_and_dash)
        a_move_to_target = Action('타겟으로 이동', self.move_to_target)
        a_idle = Action('대기', self.idle_state)

        summon_sequence = Sequence('소환 시퀀스', c_should_summon, a_summon)
        charge_and_dash = Sequence('차지 및 돌진 시퀀스', c_target_exists, c_target_nearby, a_charge_and_dash)
        chase_sequence = Sequence('추격 시퀀스', c_target_nearby, a_move_to_target)

        root = Selector('보스 AI',
                        summon_sequence,
                        charge_and_dash,
                        chase_sequence,
                        a_idle
                        )

        self.bt = BehaviorTree(root)

    def update(self, camera=None):
        if not self.is_alive:
            return

        if self.state == 'Move' or self.state == 'Dash':
            self.frame = (self.frame + MONSTER_SPEED_PPS / self.frame_width * game_framework.frame_time) % 5
        else:
            self.frame = (self.frame + MONSTER_SPEED_PPS / self.frame_width * game_framework.frame_time) % 6

        self.bt.run()
        self.hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))

        if self.is_hit:
            self.hit_effect_duration += game_framework.frame_time
            self.hit_effect_frame += 15 * game_framework.frame_time

            if self.hit_effect_duration >= 0.4 or self.hit_effect_frame >= self.hit_effect_max_frames:
                self.is_hit = False

    def get_bb(self):
        half_w = (self.width / 2) - self.width / 20
        half_h = (self.height / 2) - self.height / 5
        return (
            self.x - (half_w * max(0.4, self.hp_ratio)),
            self.y - (half_h * max(0.4, self.hp_ratio)),
            self.x + (half_w * max(0.4, self.hp_ratio)),
            self.y + (half_h * max(0.4, self.hp_ratio))
        )

    def take_damage(self, damage, attacker_x=None, attacker_y=None):
        if not self.is_alive:
            return

        self.hp -= damage
        print(f'{self.name}이(가) {damage} 데미지를 받음. 남은 HP: {self.hp}')

        self.is_hit = True
        self.hit_effect_frame = 0
        self.hit_effect_duration = 0

        if attacker_x is not None and attacker_y is not None:
            dx = self.x - attacker_x
            dy = self.y - attacker_y
            self.hit_angle = math.atan2(dy, dx)
        else:
            self.hit_angle = 0

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
        if group == 'character:Boss' and hasattr(other, 'now_hp'):
            # 넉백 방향 계산
            dx = other.x - self.x
            dy = other.y - self.y
            dist = math.sqrt(dx * dx + dy * dy) or 1.0
            nx = dx / dist
            ny = dy / dist

            current_time = get_time()

            if self.is_dashing:
                if other not in self.hit_characters_during_dash:
                    push = 5.0
                    other.x += nx * push
                    other.y += ny * push
                    try:
                        other.clamp_to_world()
                    except:
                        pass

                    other.now_hp = max(0, other.now_hp - self.dash_damage)
                    other.last_hit_time = current_time
                    other.state_machine.handle_state_event(('STUN', (nx, ny)))

                    self.hit_characters_during_dash.add(other)
            else:
                push = 5.0
                other.x += nx * push
                other.y += ny * push
                try:
                    other.clamp_to_world()
                except:
                    pass

                # 2. 데미지는 피격 쿨타임에 따라 적용
                if current_time - other.last_hit_time >= other.hit_cooldown:
                    other.now_hp = max(0, other.now_hp - self.damage)
                    other.last_hit_time = current_time

    def draw(self, camera=None):
        if not self.is_alive:
            return

        sx, sy = camera.apply(self.x, self.y) if camera else (self.x, self.y)
        zoom = camera.zoom if camera else 1.0

        if self.state == 'Idle' or self.state == 'Charge':
            frame_y = self.frame_height * 2
        else:  # Move, Dash
            frame_y = self.frame_height

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

        if self.is_hit and KingSlime.hit_effect_image:
            frame_index = int(self.hit_effect_frame) % self.hit_effect_max_frames
            effect_width = 60
            effect_height = 89
            effect_scale = max(self.width, self.height) / 60

            angle_degrees = math.degrees(self.hit_angle)

            KingSlime.hit_effect_image.clip_composite_draw(
                frame_index * effect_width, 0,
                effect_width, effect_height,
                angle_degrees, '',
                sx, sy,
                effect_width * zoom * effect_scale,
                effect_height * zoom * effect_scale
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
