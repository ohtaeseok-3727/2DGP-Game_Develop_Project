from pico2d import *
import game_framework
import game_playmode
from game_object import Tree
import game_world

bg_image = None
logo_image = None
screen_w = 1366
screen_h = 768

def init():
    global running, bg_image, logo_image, tree, sound
    running = True
    tree = Tree(screen_w // 2, screen_h - 225)
    bg_image = load_image('resource/title/title_background.png')
    logo_image = load_image('resource/title/logo.png')
    sound = load_music('resource/sound/title_music.wav')
    sound.set_volume(64)
    sound.repeat_play()



def draw():
    clear_canvas()

    if bg_image:
        bg_image.draw(screen_w // 2, screen_h // 2, screen_w, screen_h)

    if tree:
        tree.draw()

    if logo_image:
        logo_w = getattr(logo_image, 'w', None)
        logo_h = getattr(logo_image, 'h', None)
        if logo_w and logo_h:
            logo_scale = 2.0
            logo_image.draw(screen_w // 2, screen_h-400,
                            int(logo_w * logo_scale), int(logo_h * logo_scale))
        else:
            logo_image.draw(screen_w // 2, screen_h-400)

    update_canvas()

def update():
    if tree:
        tree.update()
    pass

def finish():
    global bg_image, logo_image, tree
    bg_image = None
    logo_image = None
    tree = None
    pass

def handle_events():
    events = get_events() #이벤트를 받아서 아무것도 하지않는다.
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            game_framework.change_mode(game_playmode)
