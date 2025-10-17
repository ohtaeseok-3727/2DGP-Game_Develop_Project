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
    world.append(world_map)
    world.append(character)

def update_world():
    for obj in world:
        obj.update()
    pass

def render_world():
    clear_canvas()
    for obj in world:
        obj.draw()
    update_canvas()

running = True

open_canvas()
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()