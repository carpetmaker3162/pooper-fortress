# NOTE: got rid of the rounding in find_xy_speed so that enemies
# can actually move diagonally properly. add back or use alternative
# if floatingpoint imprecision becomes a problem

import math


def sign(number):
    if number >= 0:
        return 1
    else:
        return -1

def decrement(val):
    """Adjust value based on its magnitude."""
    if abs(val) > 1:
        return sign(val)
    elif abs(val) != 0:
        return val
    else:
        return 0

def find_xy_speed(speed: float, pos: tuple, goal: tuple):
    x1, y1 = pos
    x2, y2 = goal

    dx = x2 - x1
    dy = y2 - y1

    distance = math.sqrt(dx**2 + dy**2)

    try:
        x_speed = (dx / distance) * speed
        y_speed = (dy / distance) * speed
    except ZeroDivisionError:
        return 0, 0

    return x_speed, y_speed


def distance(coords1: tuple, coords2: tuple):
    x1, y1 = coords1
    x2, y2 = coords2

    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx**2 + dy**2)


def find_nearest(entity, group):
    x1, y1 = entity.x, entity.y

    nearest_d = float("inf")
    nearest_entity = None
    for other_entity in group:
        x2, y2 = other_entity.x, other_entity.y
        d = distance((x1, y1), (x2, y2))

        if d <= nearest_d:
            nearest_d = d
            nearest_entity = other_entity

    return nearest_entity


def floor_to_nearest(coordinate: tuple, incr: tuple):
    x, y = coordinate
    incrx, incry = incr
    return (incrx * math.floor(x / incrx),
            incry * math.floor(y / incry))

def collide_aabb(entity1, entity2, offset_x=0, offset_y=0):
    left1, top1, w1, h1 = entity1.x, entity1.y, entity1.width, entity1.height
    left2, top2, w2, h2 = entity2.x, entity2.y, entity2.width, entity2.height
    
    left1 += offset_x
    top1 += offset_y
    
    right1 = left1 + w1
    right2 = left2 + w2
    bottom1 = top1 + h1
    bottom2 = top2 + h2

    return (left2 < right1 and left1 < right2
            and top2 < bottom1 and top1 < bottom2)