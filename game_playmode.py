from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera
import game_world
import game_framework
from game_object import anvil
import upgrade_mode

def handle_events():
    global running, anvil
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_f:
                if anvil.in_range(char):
                    game_framework.push_mode(upgrade_mode)
                else:
                    print("대장간이 너무 멀다")
            else:
                char.handle_event(event, game_world.camera)
        else:
            char.handle_event(event, game_world.camera)

def init():
    global char, anvil

    game_world.clear()

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    anvil = anvil()

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