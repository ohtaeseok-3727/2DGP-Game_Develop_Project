from pico2d import *

class WorldMap:
    width = 800
    height = 600
    cell = 64

    def __init__(self):
        self.image = load_image("resource/map/village_background.png")
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
    def update(self, camera=None):
        pass
    def draw(self, camera):
        for x in range(0, WorldMap.width + 1, WorldMap.cell):
            sx1, sy1 = camera.apply(x, 0)
            sx2, sy2 = camera.apply(x, WorldMap.height)
            draw_line(sx1, sy1, sx2, sy2)
        for y in range(0, WorldMap.height + 1, WorldMap.cell):
            sx1, sy1 = camera.apply(0, y)
            sx2, sy2 = camera.apply(WorldMap.width, y)
            draw_line(sx1, sy1, sx2, sy2)
        self.image.draw(WorldMap.width // 2, WorldMap.height // 2)