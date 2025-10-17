from pico2d import *
from character import character
from worldmap import WorldMap

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

def reset_world():
    global world
    global character

    world = []

    world_map = WorldMap()
    character = character()
    world.append(character)
    world.append(world_map)

def update_world():
    for obj in world:
        obj.update()
    pass