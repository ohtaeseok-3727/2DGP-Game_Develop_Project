from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            char.handle_event(event, game_world.camera)

def reset_world():
    global char

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)

    game_world.set_camera(camera)
    game_world.add_object(world_map, 0)
    game_world.add_object(char, 1)

def update_world():
    game_world.update()

def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()

running = True

open_canvas(1366, 768)
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()