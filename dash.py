import math
from pico2d import *

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

    def start(self):
        if not self.check_dash():
            return

        dx = self.character.dir
        dy = self.character.updown_dir

        # 이동 입력이 없으면 바라보는 방향을 사용
        if dx == 0 and dy == 0:
            dx = self.character.face_dir
            dy = self.character.face_updown_dir

        # 정규화해서 대각선에서도 일정속도가 나오도록 함
        length = math.hypot(dx, dy)
        if length == 0:
            # 안전 fallback: 오른쪽으로 대쉬
            nx, ny = 1.0, 0.0
        else:
            nx, ny = dx / length, dy / length

        self.vx = nx * self.speed
        self.vy = ny * self.speed
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

        if self.distance >= self.target_ditance:
            self.stop()
        pass

    def stop(self):
        if self.working:
            self.character.can_dash = max(0, self.character.can_dash - 1)
        self.working = False
        pass

    def on_input(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                self.start()
        pass