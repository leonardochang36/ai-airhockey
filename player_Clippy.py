import copy
import utils
import random

class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "Clippy"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 1
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos


    def next_move(self, current_state):
        """ Function that computes the next move of your paddle

        Implement your algorithm here. This will be the only function
        used by the GameCore. Be aware of abiding all the game rules.

        Returns:
            dict: coordinates of next position of your paddle.
        """
        if (self.my_goal == 'right'):
            if (current_state['puck_pos']['x']<((current_state['board_shape'][1]/3)*2) or current_state['goals']['right']>
                    current_state['goals']['left'] or current_state['puck_speed']['y']>140):
                if (current_state['puck_speed']['x'])<0:
                    # update my paddle pos
                    # I need to do this because GameCore moves my paddle randomly
                    self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                        else current_state['paddle2_pos']
                    self.his_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                        else current_state['paddle1_pos']

                    # estimate puck path
                    path = estimate_path(current_state, self.future_size)

                    # computing both goal centers
                    self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                           'y': current_state['board_shape'][0] / 2}
                    self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                                 'y': current_state['board_shape'][0] / 2}
                    # find if puck path is inside my interest area
                    roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
                    target_pos = {'x': (current_state['board_shape'][1] / 8) * 7,
                                  'y': (current_state['board_shape'][0] / 2)}
                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos and target_pos['x'] > (current_state['board_shape'][1] / 2) - \
                            current_state['paddle_radius']:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                          'y': self.my_paddle_pos['y'] + direction_vector['y']}

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos
                    return self.my_paddle_pos
                else:

                    # update my paddle pos
                    # I need to do this because GameCore moves my paddle randomly
                    self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                        else current_state['paddle2_pos']

                    # estimate puck path
                    path = estimate_path(current_state, self.future_size)

                    # computing both goal centers
                    self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                           'y': current_state['board_shape'][0] / 2}
                    y = random.uniform(140, 370)
                    self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                                 'y': y}

                    # find if puck path is inside my interest area
                    roi_radius = current_state['board_shape'][0] * current_state['goal_size']
                    pt_in_roi = None
                    for p in path:
                        if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                            pt_in_roi = p
                            break

                    if pt_in_roi:
                        # estimate an aiming position
                        target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.opponent_goal_center, current_state['puck_radius'],
                                               current_state['paddle_radius'])

                        # move to target position, taking into account the max. paddle speed
                        if target_pos != self.my_paddle_pos:
                            direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                                'y': target_pos['y'] - self.my_paddle_pos['y']}
                            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                for k, v in direction_vector.items()}

                            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                utils.distance_between_points(target_pos, self.my_paddle_pos))
                            direction_vector = {k: v * movement_dist
                                                for k, v in direction_vector.items()}
                            new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                              'y': self.my_paddle_pos['y'] + direction_vector['y']}

                            # check if computed new position in not inside goal area
                            # check if computed new position in inside board limits
                            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                    utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                                self.my_paddle_pos = new_paddle_pos

                    return self.my_paddle_pos
            else:
                # update my paddle pos
                # I need to do this because GameCore moves my paddle randomly
                self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                    else current_state['paddle2_pos']
                self.his_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                    else current_state['paddle1_pos']

                # estimate puck path
                path = estimate_path(current_state, self.future_size)

                # computing both goal centers
                self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                       'y': current_state['board_shape'][0] / 2}
                self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                             'y': current_state['board_shape'][0] / 2}
                if current_state['puck_pos']['x'] < current_state['paddle2_pos']['x']:
                    self.bouncePoint = {'x': (current_state['board_shape'][1] - current_state['puck_pos']['x']) *
                                             (current_state['puck_pos']['y'] / current_state['board_shape'][0] / 2)
                    if (current_state['puck_pos']['y'] < current_state['board_shape'][0] / 2)
                    else (current_state['board_shape'][1] - current_state['puck_pos']['x'] *
                          (current_state['board_shape'][0] - current_state['puck_pos']['y']) /
                          current_state['board_shape'][0] / 2),
                                        'y': current_state['board_shape'][0]
                                        if self.his_paddle_pos['y'] < current_state['board_shape'][0] / 2 else 0}
                elif (current_state['puck_pos']['x'] > current_state['paddle2_pos']['x']) and (
                        current_state['paddle2_pos']['y'] < current_state['board_shape'][0] / 2):
                    self.bouncePoint = {'x': current_state['paddle2_pos']['x'],
                                        'y': (current_state['board_shape'][0] / 6) * 5}
                else:
                    self.bouncePoint = {'x': current_state['board_shape'][1],
                                        'y': current_state['board_shape'][0] / 6}
                # find if puck path is inside my interest area
                roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
                pt_in_roi = None
                for p in path:
                    if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                        pt_in_roi = p
                        break
                if pt_in_roi:
                    # estimate an aiming position
                    if current_state['puck_pos']['x'] > (current_state['board_shape'][1] / 12) * 7:
                        target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.bouncePoint, current_state['puck_radius'],
                                               current_state['paddle_radius'])
                    else:
                        target_pos = {'x': current_state['board_shape'][1] - (current_state['board_shape'][1] / 8),
                                      'y': ((current_state['puck_pos']['y'] / 2) + (
                                              current_state['board_shape'][0] / 4))}

                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos and target_pos['x'] > (current_state['board_shape'][1] / 2) - \
                            current_state['paddle_radius']:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                          'y': self.my_paddle_pos['y'] + direction_vector['y']}

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos

                # time.sleep(2)
                # return {'x': -12, 'y': -6543}
                else:
                    target_pos = {'x': current_state['board_shape'][1] - (current_state['board_shape'][1] / 8),
                                  'y': ((current_state['puck_pos']['y'] / 3) + (
                                          current_state['board_shape'][0] / 3))}

                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos and target_pos['x'] > (current_state['board_shape'][1] / 2) - \
                            current_state['paddle_radius']:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                          'y': self.my_paddle_pos['y'] + direction_vector['y']}

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos
                return self.my_paddle_pos

        else:
            if (current_state['puck_pos']['x']>current_state['board_shape'][1]/3 or
                    current_state['goals']['left']>current_state['goals']['right'] or
                    current_state['puck_speed']['y']>140):

                if (current_state['puck_speed']['x'])>0:
                    # update my paddle pos
                    # I need to do this because GameCore moves my paddle randomly
                    self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                        else current_state['paddle2_pos']
                    self.his_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                        else current_state['paddle1_pos']

                    # estimate puck path
                    path = estimate_path(current_state, self.future_size)

                    # computing both goal centers
                    self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                           'y': current_state['board_shape'][0] / 2}
                    self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                                 'y': current_state['board_shape'][0] / 2}
                    # find if puck path is inside my interest area
                    roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
                    target_pos = {'x': (current_state['board_shape'][1] / 8),
                                  'y': (current_state['board_shape'][0] / 2)}
                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos and target_pos['x'] < (current_state['board_shape'][1] / 2) - \
                            current_state['paddle_radius']:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                          'y': self.my_paddle_pos['y'] + direction_vector['y']}

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos
                    return self.my_paddle_pos
                else:

                    self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                        else current_state['paddle2_pos']

                    # estimate puck path
                    path = estimate_path(current_state, self.future_size)

                    # computing both goal centers
                    self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                           'y': current_state['board_shape'][0] / 2}
                    self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                                 'y': current_state['board_shape'][0] / 2}

                    # find if puck path is inside my interest area
                    roi_radius = current_state['board_shape'][0] * current_state['goal_size']
                    pt_in_roi = None
                    for p in path:
                        if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                            pt_in_roi = p
                            break

                    if pt_in_roi:
                        # estimate an aiming position
                        target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.opponent_goal_center, current_state['puck_radius'],
                                               current_state['paddle_radius'])

                        # move to target position, taking into account the max. paddle speed
                        if target_pos != self.my_paddle_pos:
                            direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                                'y': target_pos['y'] - self.my_paddle_pos['y']}
                            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                for k, v in direction_vector.items()}

                            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                utils.distance_between_points(target_pos, self.my_paddle_pos))
                            direction_vector = {k: v * movement_dist
                                                for k, v in direction_vector.items()}
                            new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                              'y': self.my_paddle_pos['y'] + direction_vector['y']}

                            # check if computed new position in not inside goal area
                            # check if computed new position in inside board limits
                            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                    utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                                self.my_paddle_pos = new_paddle_pos

                    return self.my_paddle_pos
            else:
                # update my paddle pos
                # I need to do this because GameCore moves my paddle randomly
                self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                    else current_state['paddle2_pos']
                self.his_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                    else current_state['paddle1_pos']

                # estimate puck path
                path = estimate_path(current_state, self.future_size)

                # computing both goal centers
                self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                                       'y': current_state['board_shape'][0] / 2}
                self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                             'y': current_state['board_shape'][0] / 2}
                if current_state['puck_pos']['x'] > current_state['paddle1_pos']['x']:
                    self.bouncePoint = {'x': (current_state['board_shape'][1] - current_state['puck_pos']['x']) *
                                             (current_state['puck_pos']['y'] / current_state['board_shape'][0] / 2)
                    if (current_state['puck_pos']['y'] < current_state['board_shape'][0] / 2)
                    else (current_state['board_shape'][1] - current_state['puck_pos']['x'] *
                          (current_state['board_shape'][0] - current_state['puck_pos']['y']) /
                          current_state['board_shape'][0] / 2),
                                        'y': current_state['board_shape'][0]
                                        if self.his_paddle_pos['y'] < current_state['board_shape'][0] / 2 else 0}
                elif (current_state['puck_pos']['x'] < current_state['paddle1_pos']['x']) and (
                        current_state['paddle1_pos']['y'] < current_state['board_shape'][0] / 2):
                    self.bouncePoint = {'x': current_state['board_shape'][1],
                                        'y': (current_state['board_shape'][0] / 6) * 5}
                else:
                    self.bouncePoint = {'x': 0, 'y': current_state['board_shape'][0] / 6}

                # find if puck path is inside my interest area
                roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
                pt_in_roi = None
                for p in path:
                    if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                        pt_in_roi = p
                        break

                if pt_in_roi:
                    # estimate an aiming position
                    if current_state['puck_pos']['x'] < current_state['board_shape'][1] / 2:
                        target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.bouncePoint, current_state['puck_radius'],
                                               current_state['paddle_radius'])
                    else:
                        target_pos = {'x': current_state['board_shape'][1] / 8,
                                      'y': ((current_state['puck_pos']['y'] / 2) + (current_state['board_shape'][0] / 4))}

                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos and target_pos['x'] < (current_state['board_shape'][1] / 2) - \
                            current_state['paddle_radius']:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                          'y': self.my_paddle_pos['y'] + direction_vector['y']}

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos

                # time.sleep(2)
                # return {'x': -12, 'y': -6543}
                return self.my_paddle_pos


def estimate_path(current_state, after_time):
    """ Function that function estimates the next moves in a after_time window

    Returns:
        list: coordinates and speed of puck for next ticks
    """

    state = copy.copy(current_state)
    path = []
    while after_time > 0:
        state['puck_pos'] = utils.next_pos_from_state(state)
        if utils.is_goal(state) is not None:
            break
        if utils.next_after_boundaries(state):
            state['puck_speed'] = utils.next_after_boundaries(state)
        path.append((state['puck_pos'], state['puck_speed']))
        after_time -= state['delta_t']
    return path