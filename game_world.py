world = [[],[],[]]
camera = None

def set_camera(cam):
    global camera
    camera = cam

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return

    raise Exception("World 에 존재하지 않는 오브젝트를 지우려고 시도함")


def update():
    if camera:
        camera.update()

    for layer in world:
        for o in layer:
            if hasattr(o, 'update'):
                import inspect
                sig = inspect.signature(o.update)
                if len(sig.parameters) > 0:
                    o.update(camera)
                else:
                    o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw(camera)

def clear():
    for layer in world:
        layer.clear()
