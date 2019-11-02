### ./utils ###
import random
import math
from functools import wraps
import time

import numpy as np

EPSILON = 0.1
GOAL_SIZE = 0.45
PADDLE_RADIUS = 32

MAX_PADDLE_SPEED = 5
MAX_PADDLE_SPEED2 = MAX_PADDLE_SPEED ** 2

BOARD_WIDTH = 995
BOARD_HEIGHT = 512
GOAL_RADIUS = BOARD_HEIGHT * GOAL_SIZE / 2
BOARD_CENTER = np.array([BOARD_WIDTH / 2, BOARD_HEIGHT / 2])

LEFT_GOAL_CENTER = np.array([0, BOARD_HEIGHT / 2])
RIGHT_GOAL_CENTER = np.array([BOARD_WIDTH, BOARD_HEIGHT / 2])

# No change, upper quartile, lower quartile.
GOAL_EDGE_OFFSET = np.array(
    [
        np.array([0, 0]),
        np.array([0, GOAL_RADIUS * 0.25]),
        np.array([0, -GOAL_RADIUS * 0.25]),
    ]
)

GUI_CORE = None

BOTTOM_BASE_LINE = np.array(
    [
        np.array([0, BOARD_HEIGHT - PADDLE_RADIUS]),
        np.array([BOARD_WIDTH, BOARD_HEIGHT - PADDLE_RADIUS]),
    ]
)
TOP_BASE_LINE = np.array(
    [np.array([0, PADDLE_RADIUS]), np.array([BOARD_WIDTH, PADDLE_RADIUS])]
)

LEFT_BASE_LINE = np.array(
    [np.array([PADDLE_RADIUS, 0]), np.array([PADDLE_RADIUS, BOARD_HEIGHT]),]
)

RIGHT_BASE_LINE = np.array(
    [
        np.array([BOARD_WIDTH - PADDLE_RADIUS, 0]),
        np.array([BOARD_WIDTH - PADDLE_RADIUS, BOARD_HEIGHT]),
    ]
)


def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = time.monotonic_ns()
        try:
            return func(*args, **kwargs)
        finally:
            end_ = time.monotonic_ns() - start
            print(f"Total execution time: {end_ * 1000} ms")

    return _time_it


def set_gui_core(gui_core):
    global GUI_CORE
    if not gui_core is None:
        GUI_CORE = gui_core


def get_vec_from_dict(_dict, key):
    val = _dict[key]
    return np.array((val["x"], val["y"]))


def get_dict_from_vec(vec):
    return {"x": vec[0], "y": vec[1]}


def magnitude(vector):
    return np.sqrt(vector.dot(vector))


def normalize(vector):
    length = magnitude(vector)
    if length == 0:
        return vector
    return vector / length


def clamp(lower, x, upper):
    return max(min(x, upper), lower)


def magnitude_squared(vector):
    return vector.dot(vector)


def distance_between_points(point_a, point_b):
    return magnitude(point_b - point_a)


def clamp_speed_vector(current_pos, movement):
    _magnitude = magnitude(movement)
    if _magnitude > 5:
        unit = movement / _magnitude
        movement = unit * 5
    new_pos = current_pos + movement
    return {"new_pos": new_pos, "movement": movement}


def clamp_speed_point(current_pos, new_pos):
    return clamp_speed_vector(current_pos, new_pos - current_pos)


def is_puck_other_side(puck_pos, side):
    if side == "left":
        return puck_pos[0] > BOARD_WIDTH / 2
    else:
        return puck_pos[0] < BOARD_WIDTH / 2


def is_out_of_bounds(pos, side):

    # vertical
    if pos[1] < PADDLE_RADIUS or pos[1] > BOARD_HEIGHT - PADDLE_RADIUS:
        return True

    # horizontal
    if side == "left":
        if pos[0] < PADDLE_RADIUS or pos[0] > BOARD_WIDTH / 2 - PADDLE_RADIUS:
            return True

        distance = distance_between_points(pos, LEFT_GOAL_CENTER)
        if distance < GOAL_RADIUS:
            return True
    else:
        if (
            pos[0] < BOARD_WIDTH / 2 + PADDLE_RADIUS
            or pos[0] > BOARD_WIDTH - PADDLE_RADIUS
        ):
            return True

        distance = distance_between_points(pos, RIGHT_GOAL_CENTER)
        if distance < GOAL_RADIUS:
            return True

    return False


def clamp_board_vector(current_pos, movement, side, keep_direction=True):

    # print("curr_x:", current_pos["x"], "curr_y:", current_pos["y"])
    new_pos = current_pos + movement

    # print("unit_x:", unit["x"], "unit_y:", unit["y"])

    if not is_out_of_bounds(new_pos, side):
        return {"new_pos": new_pos, "movement": movement}

    _magnitude = magnitude(movement)
    unit = movement / _magnitude

    if _magnitude == 0:
        return {"new_pos": new_pos, "movement": movement}

    delta = 0
    if new_pos[1] < PADDLE_RADIUS:
        delta = PADDLE_RADIUS - new_pos[1]
    if new_pos[1] > BOARD_HEIGHT - PADDLE_RADIUS:
        delta = (BOARD_HEIGHT - PADDLE_RADIUS) - new_pos[1]

    if keep_direction:
        new_pos += unit * (delta / unit[1])
    else:
        new_pos[1] += delta

    delta = 0
    if side == "left":
        if new_pos[0] < PADDLE_RADIUS:
            delta = PADDLE_RADIUS - new_pos[0]
        if new_pos[0] > BOARD_WIDTH / 2 - PADDLE_RADIUS:
            delta = (BOARD_WIDTH / 2 - PADDLE_RADIUS) - new_pos[0]
    elif side == "right":
        if new_pos[0] < (BOARD_WIDTH / 2 + PADDLE_RADIUS):
            delta = (BOARD_WIDTH / 2 + PADDLE_RADIUS) - new_pos[0]
        if new_pos[0] > BOARD_WIDTH - PADDLE_RADIUS:
            delta = (BOARD_WIDTH - PADDLE_RADIUS) - new_pos[0]

    if keep_direction:
        new_pos += unit * (delta / unit[0])
    else:
        new_pos[0] += delta

    distance = 0
    delta = 0
    goal_pos = LEFT_GOAL_CENTER if side == "left" else RIGHT_GOAL_CENTER
    distance = distance_between_points(goal_pos, new_pos)

    if distance < GOAL_RADIUS:
        # print("tried_to_enter")
        delta = max(GOAL_RADIUS - distance, 0.1)
        # if keep_direction:
        #     ?
        # else:
        #     ?
        out = new_pos - goal_pos
        new_pos += out * delta
        new_pos = clamp_speed_point(current_pos, new_pos)["new_pos"]

    return {"new_pos": new_pos, "movement": movement}


def clamp_board_point(current_pos, new_pos, side):
    return clamp_board_vector(current_pos, new_pos - current_pos, side)


def sign_for_side(side):
    if side == "left":
        return -1
    return 1


def ensure_valid_pos(current_pos, new_pos, goal):
    new_pos = clamp_speed_point(current_pos, new_pos)["new_pos"]
    return clamp_board_point(current_pos, new_pos, goal)["new_pos"]


# recovered from: https://stackoverflow.com/a/17693146/5499386
def is_point_in_line_segment(a, b, c):
    """
        Returns wether c lies in the line segment a -> b
    """
    return abs(magnitude(c - a) + magnitude(c - b) - magnitude(a - b)) < 0.01


# retrieved from: https://stackoverflow.com/questions/14307158/how-do-you-check-for-intersection-between-a-line-segment-and-a-line-ray-emanatin
def line_ray_intersection_point(rayOrigin, rayDirection, line):
    # Ray-Line Segment Intersection Test in 2D
    # http://bit.ly/1CoxdrG
    point1 = line[0]
    point2 = line[1]
    rayDirection = normalize(rayDirection)
    v1 = rayOrigin - point1
    v2 = point2 - point1
    v3 = np.array([-rayDirection[1], rayDirection[0]])
    t1 = np.cross(v2, v1) / np.dot(v2, v3)
    t2 = np.dot(v1, v3) / np.dot(v2, v3)
    if t1 >= -0.0 and t2 >= -0.0 and t2 <= 1.0:
        return rayOrigin + t1 * rayDirection
    return None


# retrieved from: https://codereview.stackexchange.com/questions/86421/line-segment-to-circle-collision-algorithm
def line_circle_intersection_point(center, radius, point1, point2):
    # print("rad:", radius)
    segment = point2 - point1

    a = segment @ segment
    if a == 0:
        return None

    b = 2 * (segment @ (point1 - center))
    c = (point1 @ point1) + (center @ center) - 2 * (point1 @ center) - (radius ** 2)

    disc = (b ** 2) - (4 * a * c)
    if disc < 0:
        return None

    sqrt_disc = math.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)

    if t1 < 0 and t2 < 0:
        return None

    t = min(t1, t2)

    return point1 + t * segment


def get_all_rays(puck_pos, puck_movement, side, max_ray_count=100):

    sign_side = sign_for_side(side)

    pos = puck_pos.copy()
    movement = puck_movement.copy()
    rays = []
    count = 0
    prev_collision = ""
    while movement[0] * sign_side > 0 and count < max_ray_count:
        count += 1
        int_pos = pos.astype(int)

        int_pos[1] += 1
        intersection_top = line_ray_intersection_point(int_pos, movement, TOP_BASE_LINE)
        int_pos[1] -= 2
        intersection_bottom = line_ray_intersection_point(
            int_pos, movement, BOTTOM_BASE_LINE
        )
        int_pos[1] += 1

        int_pos[0] += 1
        intersection_left = line_ray_intersection_point(
            int_pos, movement, LEFT_BASE_LINE
        )
        int_pos[0] -= 2
        intersection_right = line_ray_intersection_point(
            int_pos, movement, RIGHT_BASE_LINE
        )
        int_pos[0] += 1

        prev_pos = pos.copy()
        if intersection_top is not None and prev_collision != "top":
            pos = intersection_top.copy()
            movement[1] = -movement[1]
            prev_collision = "top"

        elif intersection_bottom is not None and prev_collision != "bottom":
            pos = intersection_bottom.copy()
            movement[1] = -movement[1]
            prev_collision = "bottom"

        elif intersection_left is not None and prev_collision != "left":
            pos = intersection_left.copy()
            movement[0] = -movement[0]
            prev_collision = "left"

        elif intersection_right is not None and prev_collision != "right":
            pos = intersection_right.copy()
            movement[0] = -movement[0]
            prev_collision = "right"
        else:
            if GUI_CORE is not None:
                GUI_CORE.draw_circle(
                    (int(BOARD_WIDTH / 2), int(BOARD_HEIGHT / 2)), 20, (0, 255, 0)
                )
            # print("ERROR:", pos, movement)
            break
        #     raise Exception("No collition with any border")

        if GUI_CORE is not None:
            # print("drawing")
            GUI_CORE.draw_line(
                (int(prev_pos[0]), int(prev_pos[1])),
                (int(pos[0]), int(pos[1])),
                (255, 0, 0),
            )
        # print([prev_pos, pos])
        rays.append(np.array([prev_pos, pos]))
    # if len(rays) > 0:
    #     print(len(rays))
    return rays


def get_time_from_rays(rays, speed, endpoint=None):
    """
        Returns the ammount of frames it takes to ge to the endpoint (or the last ray)
        with the given speed
    """
    total_distance = 0
    ## create a vertical plane and intersect with that (or do the right thing and do the math)
    for ray in rays:
        start = ray[0]
        end = ray[1]
        if endpoint is not None and is_point_in_line_segment(start, end, endpoint):
            total_distance += magnitude(endpoint - start)
            break
        else:
            total_distance += magnitude(end - start)
    return total_distance / speed


def closest_point(from_pos, point_a, point_b):
    a = distance_between_points(from_pos, point_a)
    b = distance_between_points(from_pos, point_b)
    return point_a if a <= b else point_b


# Does not check for side, always go to closest line_segment in puck trajectory.
def get_closest_puck_ray(paddle_pos, rays):

    if len(rays) == 0:
        return {"closest_point": None, "closest_ray": None}

    min_distance = math.inf
    _closest_point = None
    closest_ray = None
    for ray in rays:
        closest = point_closest_point_on_line_segment(paddle_pos, ray)
        distance = distance_between_points(closest, paddle_pos)
        if distance < min_distance:
            min_distance = distance
            _closest_point = closest
            closest_ray = ray

    if not GUI_CORE is None:
        GUI_CORE.draw_line(
            (int(closest_ray[0][0]), int(closest_ray[0][1])),
            (int(closest_ray[1][0]), int(closest_ray[1][1])),
            (0, 0, 255),
        )

    return {"closest_point": _closest_point, "closest_ray": closest_ray}


def point_closest_point_on_line_segment(point, segment):
    # Check if line has length.
    rl = segment[1] - segment[0]
    squared_len = magnitude_squared(rl)
    if squared_len == 0.0:
        return segment[0]

    rp = point - segment[0]
    dot = np.dot(rp, rl) / squared_len

    if dot < 0.0:
        return segment[0]
    elif dot > 1.0:
        return segment[1]

    return segment[0] + (rl * dot)


## Aiming mechanisms.


def aim_reflect(paddle_position, ray, target):
    norm_ray = normalize(ray[0] - paddle_position)
    norm_target = normalize(target - paddle_position)
    if not GUI_CORE is None:
        GUI_CORE.draw_circle(
            (int(target[0]), int(target[1])), 10, (0, 0, 255),
        )
    alpha = math.acos(norm_ray @ norm_target) / 2
    return np.array([-math.cos(alpha), math.sin(alpha)]) * PADDLE_RADIUS


def aim_random_y_big():
    return np.array([0, random.random() * (PADDLE_RADIUS)])


def aim_random_y_small():
    return np.array([0, random.random() * (PADDLE_RADIUS / 2)])


def aim(from_pos, target_pos, current_pos):
    vector_1 = from_pos - current_pos
    vector_2 = target_pos - current_pos

    if magnitude(vector_1) == 0 or magnitude(vector_2) == 0:
        return current_pos

    vector_1 = normalize(from_pos - current_pos)
    vector_2 = normalize(target_pos - current_pos)
    if GUI_CORE is not None:
        a = 100 * (vector_1) + current_pos
        b = 100 * (vector_2) + current_pos
        GUI_CORE.draw_line(
            (int(current_pos[0]), int(current_pos[1])),
            (int(a[0]), int(a[1])),
            (0, 255, 0),
        )
        GUI_CORE.draw_line(
            (int(current_pos[0]), int(current_pos[1])),
            (int(b[0]), int(b[1])),
            (0, 255, 0),
        )
    direction_to_move = normalize(-(vector_1 + vector_2))
    return current_pos + (direction_to_move * PADDLE_RADIUS * 2)


# Helper for line_intersect calculation.
def perp(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def seg_intersect(line_a, line_b):
    da = line_a[1] - line_a[0]
    db = line_b[1] - line_b[0]
    dp = line_a[0] - line_b[0]
    dap = perp(da)
    denom = np.dot(dap, db)
    num = np.dot(dap, dp)
    return (num / denom.astype(float)) * db + line_b[0]


def aim_bounce(from_pos, target_pos, up=True, bounce=2):
    if bounce == 0:
        return target_pos

    if bounce == 1:
        reverse_from_point = np.array(
            [
                from_pos[0],
                -(from_pos[1] - PADDLE_RADIUS)
                if up
                else (2 * BOARD_HEIGHT) - from_pos[1] - PADDLE_RADIUS,
            ]
        )
        line_a = np.array([reverse_from_point, target_pos])
        if GUI_CORE is not None:
            GUI_CORE.draw_line(
                (
                    int(TOP_BASE_LINE[0][0] if up else BOTTOM_BASE_LINE[0][0]),
                    int(TOP_BASE_LINE[0][1] if up else BOTTOM_BASE_LINE[0][1]),
                ),
                (
                    int(TOP_BASE_LINE[1][0] if up else BOTTOM_BASE_LINE[1][0]),
                    int(TOP_BASE_LINE[1][1] if up else BOTTOM_BASE_LINE[1][1]),
                ),
                (0, 0, 0),
            )
            GUI_CORE.draw_line(
                (int(line_a[0][0]), int(line_a[0][1])),
                (int(line_a[1][0]), int(line_a[1][1])),
                (0, 0, 0),
            )
        return seg_intersect(line_a, TOP_BASE_LINE if up else BOTTOM_BASE_LINE)

    awkward_ray = (
        np.array(
            [
                from_pos,
                np.array(
                    [
                        target_pos[0],
                        (-BOARD_HEIGHT * (bounce - 1)) - (BOARD_HEIGHT - target_pos[1]),
                    ]
                ),
            ]
        )
        if up
        else np.array(
            [
                from_pos,
                np.array(
                    [target_pos[0], (BOARD_HEIGHT * (bounce - 1)) + target_pos[1]]
                ),
            ]
        )
    )

    if GUI_CORE is not None:
        GUI_CORE.draw_line(
            (
                int(TOP_BASE_LINE[0][0] if up else BOTTOM_BASE_LINE[0][0]),
                int(TOP_BASE_LINE[0][1] if up else BOTTOM_BASE_LINE[0][1]),
            ),
            (
                int(TOP_BASE_LINE[1][0] if up else BOTTOM_BASE_LINE[1][0]),
                int(TOP_BASE_LINE[1][1] if up else BOTTOM_BASE_LINE[1][1]),
            ),
            (0, 0, 0),
        )
        GUI_CORE.draw_line(
            (int(awkward_ray[0][0]), int(awkward_ray[0][1])),
            (int(awkward_ray[1][0]), int(awkward_ray[1][1])),
            (0, 0, 0),
        )

    return seg_intersect(awkward_ray, TOP_BASE_LINE if up else BOTTOM_BASE_LINE)


### bounce_circular_goalie.py ###
import random


class Player:
    def __init__(self, paddle_pos, goal_side, gui_core=None):
        self.my_display_name = "player_TEXEM"
        set_gui_core(gui_core)
        self.my_goal = goal_side
        self.left = goal_side == "left"
        self.right = not self.left
        self.goal_pos = LEFT_GOAL_CENTER if self.left else RIGHT_GOAL_CENTER
        self.enemy_goal_pos = LEFT_GOAL_CENTER if self.right else RIGHT_GOAL_CENTER
        self.outer_radius = GOAL_RADIUS + PADDLE_RADIUS * 3

        self.current_pos = paddle_pos
        self.enemy_pos = None
        self.aiming = None
        self.r = 0

    def kickoff(self, puck_pos):
        new_pos = puck_pos.copy()
        new_pos = ensure_valid_pos(self.current_pos, new_pos, self.my_goal)
        return get_dict_from_vec(new_pos)

    def draw_visual_feedback(self, new_pos):
        if GUI_CORE is not None:
            GUI_CORE.draw_circle((int(new_pos[0]), int(new_pos[1])), 10, (255, 0, 0))
            GUI_CORE.draw_circle(
                (int(self.goal_pos[0]), int(self.goal_pos[1])),
                int(self.outer_radius),
                (255, 0, 0),
            )
            GUI_CORE.draw_circle(
                (int(self.goal_pos[0]), int(self.goal_pos[1])),
                int(GOAL_RADIUS),
                (255, 0, 0),
            )

    def get_puck_intrtception_point(self, rays):
        new_pos = None
        from_pos = None
        intersection = None
        for ray in rays:
            intersection = line_circle_intersection_point(
                self.goal_pos, self.outer_radius, ray[0], ray[1]
            )
            if intersection is None:
                continue

            new_pos = intersection
            from_pos = ray[0]
            break
        return new_pos, from_pos, intersection

    def return_to_center(self):
        if self.left:
            new_pos = LEFT_GOAL_CENTER.copy()
            new_pos[0] += self.outer_radius
        else:
            new_pos = RIGHT_GOAL_CENTER.copy()
            new_pos[0] -= self.outer_radius
        return new_pos

    def get_position_to_aim(
        self, new_pos, from_pos, intersection, only_while_close=False,
    ):
        if from_pos is None or (
            only_while_close
            and distance_between_points(self.current_pos, new_pos)
            <= PADDLE_RADIUS * 2 + 10
        ):
            return new_pos

        # HEURISTIC.
        # Check if up or down depending on where enemy is.
        # up = self.enemy_pos[1] > (BOARD_HEIGHT / 2)

        # Random for Goal Corner quartile.
        target_pos = (
            self.enemy_goal_pos.copy() + GOAL_EDGE_OFFSET[int(random.random() * 2.49)]
        )

        up_target = aim_bounce(intersection, target_pos, up=True, bounce=self.r)
        up_where_to_be = aim(from_pos, up_target, new_pos)

        down_target = aim_bounce(intersection, target_pos, up=False, bounce=self.r)
        down_where_to_be = aim(from_pos, down_target, new_pos)

        # print(self.my_goal, "targeting up:", up_target)
        # print(self.my_goal, "targeting down:", down_target)

        if self.left:
            if up_target[0] < 0 or down_target[0] < 0:
                target = aim_bounce(from_pos, target_pos, bounce=0)
                return aim(from_pos, target, new_pos)

        if self.right:
            if up_target[0] > BOARD_WIDTH or down_target[0] > BOARD_WIDTH:
                target = aim_bounce(from_pos, target_pos, bounce=0)
                return aim(from_pos, target, new_pos)

        return (
            down_where_to_be
            if magnitude(from_pos - down_where_to_be)
            < magnitude(from_pos - up_where_to_be)
            else up_where_to_be
        )

    def next_move(self, current_state):
        self.current_pos = get_vec_from_dict(
            current_state, "paddle1_pos" if self.left else "paddle2_pos"
        )
        self.enemy_pos = get_vec_from_dict(
            current_state, "paddle1_pos" if self.left else "paddle2_pos"
        )

        puck_speed = get_vec_from_dict(current_state, "puck_speed")
        puck_pos = get_vec_from_dict(current_state, "puck_pos")

        speed_x_is_zero = abs(puck_speed[0]) < 0.01
        is_other_side = is_puck_other_side(puck_pos, self.my_goal)

        if speed_x_is_zero and not is_other_side:
            return self.kickoff(puck_pos)

        rays = get_all_rays(puck_pos, puck_speed, self.my_goal)
        sign_for_my_side = sign_for_side(self.my_goal)
        puck_coming_to_me = sign_for_my_side * puck_speed[0]

        if puck_coming_to_me > 0 and self.aiming is None:
            self.aiming = "down" if random.randint(0, 1) == 0 else "up"
            self.r = random.randint(0, 2)
            # self.r = 1
        elif puck_coming_to_me < 0:
            self.aiming = None

        new_pos, from_pos, intersection = self.get_puck_intrtception_point(rays)

        if new_pos is None:
            new_pos = self.return_to_center()

        self.draw_visual_feedback(new_pos)

        new_pos = self.get_position_to_aim(new_pos, from_pos, intersection)

        new_pos = ensure_valid_pos(self.current_pos, new_pos, self.my_goal)

        return get_dict_from_vec(new_pos)
