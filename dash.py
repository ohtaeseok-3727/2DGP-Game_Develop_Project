import math
from pico2d import *
from ctypes import *
from sdl2 import *
from worldmap import WorldMap
import game_framework

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 50.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


class dashstate:
    def __init__(self, character):
        self.character = character
        self.working = False
        self.distance = 0
        self.target_ditance = 50
        self.speed = 10
        self.vx = 0
        self.vy = 0
        self.dash_cooldown = 0.3
        self.last_dash_time = -self.dash_cooldown
        pass

    def check_dash(self):
        current_time = get_time()
        time_since_last_dash = current_time - self.last_dash_time
        return time_since_last_dash > self.dash_cooldown and self.character.can_dash > 0

    def start(self, camera=None):
        if not self.check_dash():
            return

        dx = self.character.dir
        dy = self.character.updown_dir

        if dx == 0 and dy == 0:
            return

        length = math.hypot(dx, dy)
        if length == 0:
            nx, ny = 1.0, 0.0
        else:
            nx, ny = dx / length, dy / length

        self.vx = nx * RUN_SPEED_PPS * game_framework.frame_time
        self.vy = ny * RUN_SPEED_PPS * game_framework.frame_time
        self.distance = 0.0
        self.working = True
        self.last_dash_time = get_time()
        pass

    def update(self):
        if not self.working:
            return
        prev_x, prev_y = self.character.x, self.character.y
        self.character.x += self.vx
        self.character.y += self.vy

        moved = math.hypot(self.character.x - prev_x, self.character.y - prev_y)
        self.distance += moved

        try:
            self.character.clamp_to_world()
        except Exception:
            half_w = getattr(self.character, 'frame_width', 0) / 2.0
            half_h = getattr(self.character, 'frame_height', 0) / 2.0
            self.character.x = max(half_w, min(self.character.x, WorldMap.width - half_w))
            self.character.y = max(half_h, min(self.character.y, WorldMap.height - half_h))

        if self.distance >= self.target_ditance:
            self.stop()

        pass

    def stop(self):
        if self.working:
            if self.character.can_dash == 2:
                self.character.dash_recovery_time = get_time()
            self.character.can_dash = max(0, self.character.can_dash - 1)
        self.working = False
        pass

    def on_input(self, event, camera=None):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                self.start(camera)
        pass