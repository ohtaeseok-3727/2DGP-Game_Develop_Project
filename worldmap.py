from pico2d import *

class WorldMap:
    def __init__(self, width = 1366, height = 768, cell = 64):
        self.width = width
        self.height = height
        self.cell = cell
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
    def