from pico2d import *
from sdl2 import SDL_ShowCursor, SDL_DISABLE
import title_mode as start_mode
import game_framework

open_canvas(1366, 768)

SDL_ShowCursor(SDL_DISABLE)

game_framework.run(start_mode)
close_canvas()