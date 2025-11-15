from pico2d import *
import game_framework
import game_playmode
from Attack import Attack
from weapon import weapon
import game_world
from worldmap import WorldMap
import math
import random
from item import Item


class ItemSlot:
    slot_image = None

    def __init__(self, x, y, size, item_type):
        self.x = x
        self.y = y
        self.size = size
        self.item_type = item_type
        self.hovered = False

        self.item_effects = {
            'AmuletOFAspiration': {'critical': 0.05},
            'AncientAnvil': {'ATK': 5},
            'Aquamarine': {'max_hp': 20},
            'ArtificialSpiritlfiel': {'critical_damage': 0.2},
            'AstronomicalTelescope': {'critical_damage': 0.5},
            'BlackScales': {'critical': 0.3},
            'BladeOfLight': {'ATK': 10},
            'BloodOfObrus': {'max_hp': 30},
            'BloodstoneRing': {'critical': 0.5},
            'BloodTear': {'max_hp': 50},
            'BlueBand': {'ATK': 20},
            'BlueBohoBracelet': {'critical': 0.15},
            'BlueInkBottle': {'critical_damage': 0.3},
            'BluePearl': {'max_hp': 25},
            'BlueRing': {'ATK': 5},
            'BluntBellKnife': {'critical': 0.1},
            'CrownOfPride': {'critical': 0.7}
        }

        if ItemSlot.slot_image is None:
            try:
                ItemSlot.slot_image = load_image('resource/UI/slot.png')
            except:
                ItemSlot.slot_image = None

        try:
            self.item_image = load_image(f'resource/item/{item_type}.png')
        except:
            self.item_image = None

    def is_clicked(self, mx, my):
        half = self.size // 2
        return (self.x - half < mx < self.x + half and
                self.y - half < my < self.y + half)

    def is_hovered(self, mx, my):
        half = self.size // 2
        return (self.x - half < mx < self.x + half and
                self.y - half < my < self.y + half)

    def draw(self):
        if ItemSlot.slot_image:
            ItemSlot.slot_image.draw(self.x, self.y, self.size, self.size)
        else:
            if self.hovered:
                draw_rectangle(self.x - self.size // 2, self.y - self.size // 2,
                               self.x + self.size // 2, self.y + self.size // 2)

        if self.item_image:
            self.item_image.draw(self.x, self.y, self.size - 10, self.size - 10)

    def draw_tooltip(self, font):
        if not self.hovered or not font:
            return

        tooltip_x = self.x + 80
        tooltip_y = self.y + 40

        draw_rectangle(
            tooltip_x - 100, tooltip_y - 60,
            tooltip_x + 100, tooltip_y + 20
        )

        font.draw(tooltip_x - 90, tooltip_y + 5,
                  self.item_type, (255, 255, 255))

        effects = self.item_effects.get(self.item_type, {})
        y_offset = -15
        for stat, value in effects.items():
            stat_text = f"{stat}: +{value}"
            font.draw(tooltip_x - 90, tooltip_y + y_offset,
                      stat_text, (200, 200, 200))
            y_offset -= 20


def init():
    global char, slots, all_item_types, font
    char = game_playmode.char

    all_item_types = [
        'AmuletOFAspiration', 'AncientAnvil', 'Aquamarine',
        'ArtificialSpiritlfiel', 'AstronomicalTelescope', 'BlackScales',
        'BladeOfLight', 'BloodOfObrus', 'BloodstoneRing',
        'BloodTear', 'BlueBand', 'BlueBohoBracelet',
        'BlueInkBottle', 'BluePearl', 'BlueRing',
        'BluntBellKnife', 'CrownOfPride'
    ]

    selected_items = random.sample(all_item_types, 5)

    slots = []
    center_x = get_canvas_width() // 2
    center_y = get_canvas_height() // 2
    radius = 200
    slot_size = 120

    for i in range(5):
        angle = math.radians(i * 72 - 90)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        slots.append(ItemSlot(int(x), int(y), slot_size, selected_items[i]))

    font = None
    candidates = [
        'resource/font/NanumGothic.ttf',
        'C:/Windows/Fonts/malgun.ttf',
        None
    ]
    for fp in candidates:
        try:
            font = load_font(fp, 16)
            print(f'Font loaded: {fp}')
            break
        except Exception as e:
            print(f'Font load failed: {fp} -> {e}')
            font = None

    pass

def finish():
    pass

def update():
    game_world.update()
    pass


def draw():
    clear_canvas()

    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()
    draw_rectangle(0, 0, canvas_width, canvas_height)

    for slot in slots:
        slot.draw()

    for slot in slots:
        if slot.hovered:
            slot.draw_tooltip(font)

    game_world.render_cursor()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE or event.key == SDLK_f:
                game_framework.pop_mode()
        elif event.type == SDL_MOUSEMOTION:
            mx = event.x
            my = get_canvas_height() - event.y
            for slot in slots:
                slot.hovered = slot.is_hovered(mx, my)
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mx = event.x
            my = get_canvas_height() - event.y

            for slot in slots:
                if slot.is_clicked(mx, my):
                    item = Item(0, 0, slot.item_type)
                    char.add_item(item)
                    game_framework.pop_mode()
                    return

    pass

def pause():
    pass


def resume():
    pass
