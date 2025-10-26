from pico2d import *
from character import character
from worldmap import WorldMap
from camera import Camera

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            char.handle_event(event, camera)
def reset_world():
    global world
    global char
    global camera

    world = []

    world_map = WorldMap()
    char = character()
    camera = Camera(char)
    world.append(world_map)
    world.append(char)

def update_world():
    camera.update()
    for obj in world:
        if isinstance(obj, character):
            obj.update(camera)
        else:
            obj.update()
    pass

def render_world():
    clear_canvas()
    for obj in world:
        obj.draw(camera)
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