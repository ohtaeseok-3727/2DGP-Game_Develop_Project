from pico2d import *

class WorldMap:
    width = 1366
    height = 768
    cell = 64

    def __init__(self):
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
    def update(self):
        pass
    def draw(self):
        for x in range(0, WorldMap.width+1, WorldMap.cell):
            draw_line(x, 0, x, WorldMap.height)
        for y in range(0, WorldMap.height+1, WorldMap.cell):
            draw_line(0, y, WorldMap.width, y)