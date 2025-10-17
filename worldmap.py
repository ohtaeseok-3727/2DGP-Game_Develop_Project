from pico2d import *

class WorldMap:
    def __init__(self, width = 1366, height = 768, cell = 64):
        self.width = width
        self.height = height
        self.cell = cell
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
    def draw(self):
        for x in range(0, self.width+1, self.cell):
            draw_line(x, 0, x, self.cell)
        for y in range(0, self.height+1, self.cell):
            draw_line(0, y, self.cell, y)