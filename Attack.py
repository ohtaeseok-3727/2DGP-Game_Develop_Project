from pico2d import *
from sdl2 import SDL_MOUSEBUTTONUP, SDL_BUTTON_LEFT, SDL_MOUSEBUTTONDOWN
import math
import ctypes
from sdl2.mouse import SDL_GetMouseState

import game_framework
from worldmap import WorldMap
import game_world

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
ATTACK_SPEED_KMPH = 100.0  # Km / Hour
ATTACK_SPEED_MPM = (ATTACK_SPEED_KMPH * 1000.0 / 60.0)
ATTACK_SPEED_MPS = (ATTACK_SPEED_MPM / 60.0)
ATTACK_SPEED_PPS = (ATTACK_SPEED_MPS * PIXEL_PER_METER)


class AttackVisual:
    def __init__(self, attack):
        self.attack = attack
        self.bb_list = []  # 여러 개의 바운딩 박스 리스트
        self.num_boxes = 3  # 바운딩 박스 개수 (조절 가능)
        self.damage = attack.damage
        self.hit_targets = set()


    def update(self, camera=None):
        if not self.attack.active:
            return
        self.update_bb()

    def update_bb(self):
        atk = self.attack
        if not atk.active:
            self.bb_list = []
            return []

        if atk.character.weapon_rank == 1:
            # 원거리 공격: 단일 박스
            draw_x = atk.attack_x
            draw_y = atk.attack_y
            half_w = atk.attack_frame_width / 2
            half_h = atk.attack_frame_height / 2

            self.bb_list = [[
                (draw_x - half_w, draw_y - half_h),
                (draw_x + half_w, draw_y - half_h),
                (draw_x + half_w, draw_y + half_h),
                (draw_x - half_w, draw_y + half_h)
            ]]
        else:
            # 근접 공격: 하나의 박스
            offset_x = math.cos(atk.attack_angle) * 25
            offset_y = math.sin(atk.attack_angle) * 25

            base_x = atk.character.x + offset_x
            base_y = atk.character.y + offset_y

            full_w = (atk.attack_frame_width * atk.attack_range)
            full_h = (atk.attack_frame_height * atk.attack_range)

            draw_angle = atk.attack_angle - math.pi / 2
            cos_a = math.cos(draw_angle)
            sin_a = math.sin(draw_angle)

            # 전체 크기의 반
            half_w = full_w / 2
            half_h = full_h / 2

            # 4개 꼭짓점
            corners = [
                (-half_w, -half_h),
                (half_w, -half_h),
                (half_w, half_h),
                (-half_w, half_h)
            ]

            box_corners = []
            for px, py in corners:
                rx = px * cos_a - py * sin_a
                ry = px * sin_a + py * cos_a
                box_corners.append((base_x + rx, base_y + ry))

            self.bb_list = [box_corners]

        return self.bb_list
    def get_bb(self):
        atk = self.attack
        if not atk.active:
            return 0, 0, 0, 0

        if not self.bb_list:
            return 0, 0, 0, 0

        # 모든 바운딩 박스를 포함하는 AABB 계산
        all_x = []
        all_y = []

        for box in self.bb_list:
            for x, y in box:
                all_x.append(x)
                all_y.append(y)

        if not all_x:
            return 0, 0, 0, 0

        return min(all_x), min(all_y), max(all_x), max(all_y)

    def handle_collision(self, group, other):
        if other in self.hit_targets:
            return

        # 이미 죽은 몬스터는 무시
        if hasattr(other, 'is_alive') and not other.is_alive:
            return

        if 'attack:monster' in group:
            if hasattr(other, 'take_damage'):
                other.take_damage(self.damage)
                self.hit_targets.add(other)

    def draw(self, camera=None):
        atk = self.attack
        if not atk.active:
            return

        zoom = camera.zoom if camera else 1.0

        # 공격 스프라이트 그리기 (기존 코드)
        if atk.character.weapon_rank == 1:
            draw_x = atk.attack_x
            draw_y = atk.attack_y
            sx, sy = (camera.apply(draw_x, draw_y)) if camera else (draw_x, draw_y)

            Attack.motion.clip_composite_draw(
                atk.current_frame * atk.attack_frame_width, 0,
                atk.attack_frame_width, atk.attack_frame_height,
                0, '',
                sx, sy,
                atk.attack_frame_width * zoom, atk.attack_frame_height * zoom
            )
        else:
            offset_x = math.cos(atk.attack_angle) * 25
            offset_y = math.sin(atk.attack_angle) * 25

            draw_x = atk.character.x + offset_x
            draw_y = atk.character.y + offset_y

            sx, sy = (camera.apply(draw_x, draw_y)) if camera else (draw_x, draw_y)
            draw_angle = atk.attack_angle - math.pi / 2

            Attack.motion.clip_composite_draw(
                atk.current_frame * atk.attack_frame_width, 0,
                atk.attack_frame_width, atk.attack_frame_height,
                draw_angle, '',
                sx, sy,
                atk.attack_frame_width * zoom * atk.attack_range,
                atk.attack_frame_height * zoom * atk.attack_range
            )

        # 모든 바운딩 박스 그리기
        if self.attack.active and self.bb_list:
            for box_corners in self.bb_list:
                if camera:
                    screen_corners = [camera.apply(x, y) for x, y in box_corners]
                else:
                    screen_corners = box_corners

                for i in range(4):
                    x1, y1 = screen_corners[i]
                    x2, y2 = screen_corners[(i + 1) % 4]
                    draw_line(x1, y1, x2, y2)

class Attack:
    motion = None
    def __init__(self, character):
        self.character = character
        self.attack_frame = 0
        self.attack_speed = 0
        self.attack_time = 0
        self.max_attack_count = 0
        self.attack_count = 0
        self.attack_frame_width = 0
        self.attack_frame_height = 0
        self.current_frame = 0
        self.current_frame_f = 0.0
        self.release_requested = False
        self.active = False
        self.attack_angle = 0

        self.attack_x = 0
        self.attack_y = 0
        self.attack_range = 1

        self.is_combo_count = False
        self.combo_count = 0
        self.combo_trigger_frame = 4

        self.attack_cooldown = 0.7
        self.last_attack_time = -self.attack_cooldown

        self.visual = None


        if self.character.weapon_type == 'katana' and self.character.weapon_rank == 0:
            Attack.motion = load_image('resource/weapon/katana/katana_default_sprite_sheet.png')
            self.attack_frame = 8
            self.attack_speed = 15
            self.max_attack_count = 1
            self.attack_frame_width = 60
            self.attack_frame_height = 133
            self.attack_range = 1
            self.attack_speed_pps = ATTACK_SPEED_PPS * 1.0
        elif self.character.weapon_type == 'katana' and self.character.weapon_rank == 1:
            Attack.motion = load_image('resource/weapon/katana/katana_Hou_swing_sprite_sheet.png')
            self.attack_frame = 11
            self.attack_speed = 40
            self.max_attack_count = 1
            self.attack_frame_width = 79
            self.attack_frame_height = 79
            self.attack_speed_pps = ATTACK_SPEED_PPS * 2.0
        elif self.character.weapon_type == 'katana' and self.character.weapon_rank == 2:
            Attack.motion = load_image('resource/weapon/katana/katana_default_sprite_sheet.png')
            self.attack_frame = 8
            self.attack_speed = 33
            self.max_attack_count = 2
            self.attack_frame_width = 60
            self.attack_frame_height = 133
            self.combo_trigger_frame = 4
            self.attack_range = 1.5
            self.attack_speed_pps = ATTACK_SPEED_PPS * 1.4
            #근접 참격 강화 모션

        self.damage = self.character.ATK * self.character.weapon.attack_coefficient

    def can_attack(self):
        current_time = get_time()
        time_since_last_attack = current_time - self.last_attack_time
        if time_since_last_attack >= self.attack_cooldown:
            return True
        return False

    def start(self, camera=None):
        if not self.can_attack():
            return

        # 기존 visual이 있으면 완전히 제거
        if self.visual is not None:
            try:
                game_world.remove_collision_object(self.visual)
                game_world.remove_object(self.visual)
            except Exception:
                pass
            finally:
                self.visual = None

        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        screen_x = x.value
        screen_y = get_canvas_height() - y.value

        if camera:
            world_x, world_y = camera.screen_to_world(screen_x, screen_y)
        else:
            world_x = screen_x
            world_y = screen_y

        if self.character.weapon_rank == 1:
            self.attack_x = world_x
            self.attack_y = world_y
        else:
            delta_x = world_x - self.character.x
            delta_y = world_y - self.character.y
            self.attack_angle = math.atan2(delta_y, delta_x)

        self.active = True
        self.attack_time = get_time()
        self.current_frame = 0
        self.current_frame_f = 0.0
        self.release_requested = False
        self.last_attack_time = get_time()

        if self.character.weapon_rank == 2 :
            self.combo_count += 1
            self.is_combo_count = True

        try:
            if self.visual is None:
                self.visual = AttackVisual(self)
                game_world.add_object(self.visual, 2)

                for obj in game_world.world[2]:
                    if hasattr(obj, 'take_damage') and obj != self.visual:
                        game_world.add_collision_pairs('attack:monster', self.visual, obj)
            else:
                # 재사용 시 hit_targets 초기화
                self.visual.hit_targets.clear()
                self.visual.damage = self.damage
        except Exception:
            print(f"AttackVisual 생성 오류: {e}")
            self.visual = None

    def stop(self):
        self.active = False
        self.release_requested = False

        try:
            if self.visual is not None:
                game_world.remove_collision_object(self.visual)
                game_world.remove_object(self.visual)
                self.visual = None
        except Exception as e:
            print(f"AttackVisual 제거 오류: {e}")
            self.visual = None

        if self.character.weapon_rank == 2:
            if self.combo_count >= self.max_attack_count:
                self.combo_count = 0
                self.is_combo_active = False

    def on_input(self, event, camera=None):
        if event.type == SDL_MOUSEBUTTONUP and event.button == SDL_BUTTON_LEFT:
            self.release_requested = True
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            self.start(camera)
            self.release_requested = False
        pass

    def update(self):
        if not self.active:
            return

        if self.attack_frame_width>0:
            frames_per_second = self.attack_speed_pps / self.attack_frame_width
        else:
            frames_per_second = 0.0

        prev_frame_int = self.current_frame
        self.current_frame_f += frames_per_second * game_framework.frame_time
        self.current_frame = int(self.current_frame_f)

        if self.character.weapon_rank == 2:
            if self.current_frame == self.combo_trigger_frame and self.combo_count < self.max_attack_count:
                self.current_frame = 0
                self.current_frame_f = 0.0
                self.combo_count += 1
            elif self.current_frame >= self.attack_frame:
                self.stop()
        else:
            if self.current_frame >= self.attack_frame:
                self.stop()
        pass

    def draw(self, camera=None):
        pass
