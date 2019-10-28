""" Useful functions

This module implements several useful functions that you might want to reuse.
Some of these functions implements the oficial rules of the challenge.

"""


def next_pos_from_state(state):
    """ Function that computes the next puck position

    From the current state, the next position of the puck is computed
    but not set.

    Returns:
        dict: coordinates
    """
    xn = state['puck_pos']['x'] + state['puck_speed']['x'] * state['delta_t']
    yn = state['puck_pos']['y'] + state['puck_speed']['y'] * state['delta_t']
    return {'x': xn, 'y': yn}


def next_after_boundaries(state):
    """ Function that computes the next speed after bounce

    If current puck position implies a bounce, the next puck speed
    is computed based on against which border the bounce occurs.
    e.g., horizontal or vertical.

    Returns:
        dict: speed components in x and y
    """
    if is_out_of_boundaries(state) == 'horizontal':
        return {'x': state['puck_speed']['x'] * -1, 'y': state['puck_speed']['y']}
    if is_out_of_boundaries(state) == 'vertical':
        return {'x': state['puck_speed']['x'], 'y': state['puck_speed']['y'] * -1}
    return None


def is_out_of_boundaries(state):
    """ Function that detects if the puck is out of the board limits.

    Returns:
        None: if is not out of the boundaries
        str: 'horizontal' or 'vertical' if is out of boundaries.
    """
    if next_pos_from_state(state)['x'] + state['puck_radius'] >= state['board_shape'][1] \
       or next_pos_from_state(state)['x'] - state['puck_radius'] <= 0:
        return 'horizontal'
    if next_pos_from_state(state)['y'] + state['puck_radius'] >= state['board_shape'][0] \
       or next_pos_from_state(state)['y'] - state['puck_radius'] <= 0:
        return 'vertical'
    return None


def is_out_of_boundaries_paddle(paddle_pos, state):
    """ Function that detects if a paddle is out of the board limits.

    Returns:
        None: if is not out of the boundaries
        str: 'horizontal' or 'vertical' if is out of boundaries.
    """
    if paddle_pos['x'] + state['paddle_radius'] >= state['board_shape'][1] \
       or paddle_pos['x'] - state['paddle_radius'] <= 0:
        return 'horizontal'
    if paddle_pos['y'] + state['paddle_radius'] >= state['board_shape'][0] \
       or paddle_pos['y'] - state['paddle_radius'] <= 0:
        return 'vertical'
    return None


def is_inside_goal_area_paddle(paddle_pos, state):
    """ Function that detects if a paddle is the goal area.

    Returns:
        bool: eval result
    """

    goal_size = state['goal_size'] * state['board_shape'][0] / 2
    if distance_between_points(paddle_pos, {'x': 0, 'y': state['board_shape'][0]/2}) < goal_size:
        return True

    if distance_between_points(paddle_pos, {'x': state['board_shape'][1],
                                            'y': state['board_shape'][0]/2}) < goal_size:
        return True

    return False


def is_goal(state):
    """ Function that detects if the puck is inside the goal area.

    Returns:
        None: if is not goal
        str: 'left' or 'right' according to the goal area if positive for goal.
    """

    if is_out_of_boundaries(state) == 'horizontal':
        if state['puck_pos']['y'] > state['board_shape'][0] * (1 - state['goal_size']) / 2 and \
             state['puck_pos']['y'] < state['board_shape'][0] * (1 + state['goal_size']) / 2:
            if state['puck_pos']['x'] < state['board_shape'][1] / 2:
                return 'right'
            else:
                return 'left'
    return None


def distance_between_points(p1, p2):
    """ Function that computes the euclidean distance between to points.

    Returns:
        float: distance value
    """
    return ((p1['x']-p2['x']) * (p1['x'] - p2['x']) + (p1['y']-p2['y']) * (p1['y']-p2['y'])) ** 0.5


def detect_collision(state, pos2, r2):
    """ Function that detects if the puck collided with a paddle of pos2 and r2 radius

    Returns:
        bool: True if collision occurred, False if not
    """
    return bool(distance_between_points(next_pos_from_state(state),
                                        pos2) <= state['puck_radius'] + r2)


def vector_l2norm(v):
    """ Function that computes the L2 norm (magnitude) of a vector.

    Returns:
        float: magnitude value
    """
    return (v['x']*v['x'] + v['y']*v['y']) ** 0.5


def next_speed_after_collision(pos1, speed1, pos2, speed2):
    """ Function that computes the resulting speed of the puck after collision.

    Returns:
        dict: speed components in x and y of puck
    """

    # vector perpendicular to (x, y) is (-y, x)
    tangent_vector = {'x': pos2['y'] - pos1['y'], 'y': pos1['x'] - pos2['x']}

    # normalize vector
    tangent_vector_l2norm = vector_l2norm(tangent_vector)
    tangent_vector = {k: v/tangent_vector_l2norm for k, v in tangent_vector.items()}

    # performing the dot product of the relative velocity vector and the tangent vector
    # gives us the length of the velocity component parallel to the tangent
    relative_speed = {'x': speed1['x'] - speed2['x'], 'y': speed1['y'] - speed2['y']}
    length = relative_speed['x'] * tangent_vector['x'] + relative_speed['y'] * tangent_vector['y']

    # multiply the normalized tangent vector by the length to get
    # the vector component parallel to the tangent
    speed_on_tangent = {k: v * length for k, v in tangent_vector.items()}

    # subtracting the velocity component parallel to the tangent from the
    # relative velocity gives us the velocity component perpendicular to the tangent
    speed_perpendicular_to_tangent = {'x': relative_speed['x'] - speed_on_tangent['x'],
                                      'y': relative_speed['y'] - speed_on_tangent['y']}

    # to perform the collision
    # the velocity component perpendicular to the tangent should be applied twice
    return {'x': speed1['x'] - 2 * speed_perpendicular_to_tangent['x'],
            'y': speed1['y'] - 2 * speed_perpendicular_to_tangent['y']}


def next_speed(state):
    """ Function that computes the resulting speed of the puck after move.

    Returns:
        dict: speed components in x and y of puck
    """
    if next_after_boundaries(state):
        return next_after_boundaries(state)

    if detect_collision(state, state['paddle1_pos'], state['paddle_radius']):
        return next_speed_after_collision(state['puck_pos'], state['puck_speed'],
                                          state['paddle1_pos'], state['paddle1_speed'])
    if detect_collision(state, state['paddle2_pos'], state['paddle_radius']):
        return next_speed_after_collision(state['puck_pos'], state['puck_speed'],
                                          state['paddle2_pos'], state['paddle2_speed'])
    return state['puck_speed']


def aim(pos, speed, pos_target, puck_radius, paddle_radius):
    """ Function that computes where to put the paddle for a target puck position

    Args:
        pos: puck position
        speed: puck speed
        pos_target: target position of puck

    Returns:
        dict: paddle position to achieve puck target position
    """

    # target direction vector, normalized, opposite direction
    dir_vector = {'x': pos_target['x'] - pos['x'], 'y': pos_target['y'] - pos['y']}
    dir_vector = {k: -1 * v / vector_l2norm(dir_vector) for k, v in dir_vector.items()}

    # normalized puck speed
    speed_n = {k: v / vector_l2norm(speed)  for k, v in speed.items()}

    #
    intersection_vector = {'x': dir_vector['x'] + speed_n['x'], 'y': dir_vector['y'] + speed_n['y']}
    intersection_vector = {k: v / vector_l2norm(intersection_vector)
                           for k, v in intersection_vector.items()}

    # length of collision point from pos
    intersection_vector = {k: v * (puck_radius + paddle_radius)
                           for k, v in intersection_vector.items()}

    #
    return {'x': pos['x'] + intersection_vector['x'], 'y': pos['y'] + intersection_vector['y']}


def round_point_as_tuple(pt):
    return (int(round(pt['x'])), int(round(pt['y'])))


def nearest_point_in_circle(center, r, point):
    """ Function that computes the nearest point in circle to a given point
    """
    v = {'x': point['x'] - center['x'], 'y': point['y'] - center['y']}
    px = center['x'] + r * v['x'] / vector_l2norm(v)
    py = center['y'] + r * v['y'] / vector_l2norm(v)
    return {'x': px, 'y': py}
