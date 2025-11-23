from pico2d import load_image

class WorldMap:
    _instance = None
    maps = {
        'default': 'resource/map/village_background.png',
        'boss map': 'resource/map/boss_map_background.png'
    }
    width = 800
    height = 600

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WorldMap, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.image = None
            self.width = 0
            self.height = 0
            self.change_map('default')
            self.initialized = True

    def change_map(self, map_name):
        map_path = self.maps.get(map_name)
        if map_path:
            self.image = load_image(map_path)
            self.width = self.image.w
            self.height = self.image.h
        else:
            print(f"'{map_name}'에 해당하는 맵을 찾을 수 없습니다.")

    def draw(self, camera=None):
        if camera:
            screen_x, screen_y = camera.apply(0, 0)
            zoom = camera.zoom
            self.image.draw(screen_x + (self.width * zoom) / 2,
                            screen_y + (self.height * zoom) / 2,
                            self.width * zoom,
                            self.height * zoom)
        else:
            self.image.draw(self.width // 2, self.height // 2)

    def update(self):
        pass