import math

from pico2d import get_time


class dashstate :
    def __init__(self, character):
        self.character = character
        self.fps = 30
        self.frame_time = 0
        self.working = False
        self.move_distance = 0
        self.speed = 10
        self.vx = 0
        self.vy = 0
        pass
    def enter(self, e):
        if self.character.can_dash <=0:
            self.working = False
            return
        self.working = True
        self.frame_time = get_time()
        self.startx = self.character.x
        self.starty = self.character.y
        self.move_distance = 0.0

        dx = self.character.dir
        dy = self.character.updown_dir
        if dx == 0 and dy == 0 :
            dx = self.character.face_dir
            dy = self.character.face_updown_dir
        length = math.hypot(dx, dy)
        if length == 0:
            dx,dy=1,0
            length = 1

        self.vx = (dx/length)*self.speed
        self.vy = (dy/length)*self.speed
        pass
    def exit(self, e):
        if self.working:
            self.character.can_dash -=1
        pass
    def do(self):
        if not self.working:
            self.character.state_machine.handle_state_event(('STOP', 0))
            return
        prev_x, prev_y = self.character.x, self.character.y
        self.character.x += self.vx
        self.character.y += self.vy
        moved = math.hypot(self.character.x - prev_x, self.character.y - prev_y)
        self.move_distance += moved
        if get_time() - self.frame_time > 1.0 / self.fps:
            self.character.frame = (self.character.frame + 1) % 8
            self.frame_time = get_time()
        if self.move_distance >= 50.0:
            self.character.state_machine.handle_state_event(('STOP', 0))
        pass
    def draw(self, camera=None):
        sx, sy = (camera.apply(self.character.x, self.character.y)) if camera else (self.character.x, self.character.y)
        zoom = camera.zoom if camera else 1.0

        if self.character.face_dir == 1 and self.character.face_updown_dir == -1:
            self.character.image.clip_draw(self.character.frame * 18, 19,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == -1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 19,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        if self.character.face_dir == 1 and self.character.face_updown_dir == 1:
            self.character.image.clip_draw(self.character.frame * 18, 0,
                                           18, 19,
                                           sx, sy,
                                           18 * zoom, 19 * zoom)
        if self.character.face_dir == -1 and self.character.face_updown_dir == 1:
            self.character.image.clip_composite_draw(self.character.frame * 18, 0,
                                                     18, 19,
                                                     0, 'h',
                                                     sx, sy,
                                                     18 * zoom, 19 * zoom)
        pass
