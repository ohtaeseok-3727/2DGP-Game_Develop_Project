from pico2d import *
from sdl2 import SDL_MOUSEBUTTONUP, SDL_BUTTON_LEFT, SDL_MOUSEBUTTONDOWN
import math
import ctypes
from sdl2.mouse import SDL_GetMouseState
from worldmap import WorldMap

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
        self.frame_time = 0
        self.release_requested = False
        self.active = False
        self.attack_angle = 0
        if self.character.weapon_type == 'katana' and self.character.weapon_rank == 0:
            Attack.motion = load_image('resource/weapon/katana/katana_default_sprite_sheet.png')
            self.attack_frame = 8
            self.attack_speed = 10
            self.max_attack_count = 1
            self.attack_frame_width = 60
            self.attack_frame_height = 133
        if self.character.weapon_type == 'katana' and self.character.weapon_rank == 1:
            Attack.motion = load_image('resource/weapon/katana/katana_hou_sprite_sheet.png')
            self.attack_frame = 11
            self.attack_speed = 8
            self.max_attack_count = 1
            self.attack_frame_width = 79
            self.attack_frame_height = 79
        if self.character.weapon_type == 'katana' and self.character.weapon_rank == 2:
            self.max_attack_count = 2
            #근접 참격 강화 모션

    def start(self, camera=None):
        x=ctypes.c_int(0)
        y=ctypes.c_int(0)
        SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        screen_x = x.value
        screen_y = get_canvas_height() - y.value

        mouse_x, mouse_y = x.value, WorldMap.height - y.value

        if camera :
            world_x = screen_x + camera.x
            world_y = screen_y + camera.y
        else :
            world_x = screen_x
            world_y = screen_y

        delta_x = world_x - self.character.x
        delta_y = world_y - self.character.y
        self.attack_angle = math.atan2(delta_y, delta_x)

        self.active = True
        self.attack_time = get_time()
        self.frame_time = get_time()
        self.current_frame = 0
        self.release_requested = False
        pass

    def stop(self):
        self.active = False
        self.release_requested = False
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

        if get_time() - self.frame_time > 1.0 / self.attack_speed:
            self.current_frame += 1
            self.frame_time = get_time()

        if self.current_frame >= self.attack_frame:
            if self.release_requested:
                self.stop()
            else:
                self.stop()

        pass
    def draw(self, camera=None):
        if not self.active:
            return
        sx, sy = (camera.apply(self.character.x, self.character.y)) if camera else (self.character.x, self.character.y)
        draw_angle = self.attack_angle - math.pi / 2

        Attack.motion.clip_composite_draw(
            self.current_frame * self.attack_frame_width, 0,
            self.attack_frame_width, self.attack_frame_height,
            draw_angle, '',
            sx, sy,
            self.attack_frame_width, self.attack_frame_height
        )
        pass
