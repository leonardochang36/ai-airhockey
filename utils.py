def next_pos_from_state(state):
    xn = state['puck_pos']['x'] + state['puck_speed']['x'] * state['delta_t']
    yn = state['puck_pos']['y'] + state['puck_speed']['y'] * state['delta_t']
    return {'x': xn, 'y': yn}


def next_after_boundaries(state):
    if is_out_of_boundaries(state) == 'horizontal':
        return {'x': state['puck_speed']['x'] * -1, 'y': state['puck_speed']['y']}
    if is_out_of_boundaries(state) == 'vertical':
        return {'x': state['puck_speed']['x'], 'y': state['puck_speed']['y'] * -1}
    return None


def is_out_of_boundaries(state):
    if next_pos_from_state(state)['x'] + state['puck_radius'] >= state['board_shape'][1] \
       or next_pos_from_state(state)['x'] - state['puck_radius'] <= 0:
        return 'horizontal'
    if next_pos_from_state(state)['y'] + state['puck_radius'] >= state['board_shape'][0] \
       or next_pos_from_state(state)['y'] - state['puck_radius'] <= 0:
        return 'vertical'
    return None


def is_out_of_boundaries_paddle(paddle_pos, state):
    if paddle_pos['x'] + state['paddle_radius'] >= state['board_shape'][1] \
       or paddle_pos['x'] - state['paddle_radius'] <= 0:
        return 'horizontal'
    if paddle_pos['y'] + state['paddle_radius'] >= state['board_shape'][0] \
       or paddle_pos['y'] - state['paddle_radius'] <= 0:
        return 'vertical'
    return None


def is_goal(state):
    if is_out_of_boundaries(state) == 'horizontal':
        if state['puck_pos']['y'] > state['board_shape'][0] * (1 - state['goal_size']) / 2 and \
             state['puck_pos']['y'] < state['board_shape'][0] * (1 + state['goal_size']) / 2:
            if state['puck_pos']['x'] < state['board_shape'][1] / 2:
                return 'left'
            else:
                return 'right'
    return None


def distance_between_points(p1, p2):
    return ((p1['x']-p2['x']) * (p1['x'] - p2['x']) + (p1['y']-p2['y']) * (p1['y']-p2['y'])) ** 0.5


def detect_collision(state, pos2, r2):
    # TODO revisar esta parte
    return bool(distance_between_points(next_pos_from_state(state), pos2) <= state['puck_radius'] + r2)


def vector_l2norm(v):
    return (v['x']*v['x'] + v['y']*v['y']) ** 0.5


def next_speed_after_collision(pos1, speed1, pos2, speed2):
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
