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
    def update(self, camera=None):
        pass
    def draw(self, camera=None):
        atk = self.attack
        if not atk.active:
            return
        zoom = camera.zoom if camera else 1.0

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
                atk.attack_frame_width * zoom * atk.attack_range, atk.attack_frame_height * zoom * atk.attack_range
            )
        pass
    def 

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

    def can_attack(self):
        current_time = get_time()
        time_since_last_attack = current_time - self.last_attack_time
        if time_since_last_attack >= self.attack_cooldown:
            return True
        return False

    def start(self, camera=None):
        if not self.can_attack():
            return
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
        pass
        try:
            if self.visual is None:
                self.visual = AttackVisual(self)
                game_world.add_object(self.visual, 2)
        except Exception:
            self.visual = None

    def stop(self):
        self.active = False
        self.release_requested = False

        try:
            if self.visual is not None:
                game_world.remove_object(self.visual)
        except Exception:
            pass
        finally:
            self.visual = None

        if self.character.weapon_rank == 2:
            if self.combo_count >= self.max_attack_count:
                self.combo_count = 0
                self.is_combo_active = False
        pass

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
