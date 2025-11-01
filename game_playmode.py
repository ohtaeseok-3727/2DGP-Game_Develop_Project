from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
import object

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            char.handle_event(event, game_world.camera)

def init():
    global char

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    anvil = object.anvil()

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 1)
    game_world.add_object(anvil, 1)

def update():
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def pause():
    pass

def resume():
    pass