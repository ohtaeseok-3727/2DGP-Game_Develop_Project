from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap

def init():
    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()
    game_world.render()
    game_world.render_cursor()
    update_canvas()


def handle_events():
    pass

def pause():
    pass


def resume():
    pass
