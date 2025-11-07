world = [[],[],[]]
camera = None

def set_camera(cam):
    global camera
    camera = cam

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def remove_collision_object(o):
    for pair in collision_pair.values():
        if o in pair[0]:
            pair[0].remove(o)
        if o in pair[1]:
            pair[1].remove(o)

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

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True


def collide_obb(a, b):
    """다중 바운딩 박스 OBB 충돌 검사"""
    # AttackVisual 객체의 다중 바운딩 박스 처리
    if hasattr(a, 'bb_list') and a.bb_list:
        boxes_a = a.bb_list
    else:
        left, bottom, right, top = a.get_bb()
        boxes_a = [[
            (left, bottom), (right, bottom),
            (right, top), (left, top)
        ]]

    if hasattr(b, 'bb_list') and b.bb_list:
        boxes_b = b.bb_list
    else:
        left, bottom, right, top = b.get_bb()
        boxes_b = [[
            (left, bottom), (right, bottom),
            (right, top), (left, top)
        ]]

    def get_axes(corners):
        axes = []
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])
            length = (normal[0] ** 2 + normal[1] ** 2) ** 0.5
            if length > 0:
                axes.append((normal[0] / length, normal[1] / length))
        return axes

    def project(corners, axis):
        dots = [c[0] * axis[0] + c[1] * axis[1] for c in corners]
        return min(dots), max(dots)

    def check_box_collision(box_a, box_b):
        axes = get_axes(box_a) + get_axes(box_b)

        for axis in axes:
            min_a, max_a = project(box_a, axis)
            min_b, max_b = project(box_b, axis)

            if max_a < min_b or max_b < min_a:
                return False
        return True

    # 모든 박스 조합 검사
    for box_a in boxes_a:
        for box_b in boxes_b:
            if check_box_collision(box_a, box_b):
                return True

    return False


collision_pair = {} # key : 충돌 종류, value : [a객체 리스트, b객체 리스트]

def add_collision_pairs(group, a, b):
    if group not in collision_pair:
        print(f'Added new group: {group}')
        collision_pair[group] = [[], []]
    if a:
        collision_pair[group][0].append(a)
    if b:
        collision_pair[group][1].append(b)

def handle_collisions():
    for group, pairs in collision_pair.items():
        for a in pairs[0]:
            for b in pairs[1]:
                # 공격 충돌은 OBB 사용
                if hasattr(a, 'bb_corners') or hasattr(b, 'bb_corners'):
                    if collide_obb(a, b):
                        a.handle_collision(group, b)
                        b.handle_collision(group, a)
                # 일반 충돌은 AABB 사용
                elif collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)