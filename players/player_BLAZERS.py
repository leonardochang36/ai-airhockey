""" Player module

This is a template/example class for your player.
This is the only file you should modify.

The logic of your hockey robot will be implemented in this class.
Please implement the interface next_move().

The only restrictions here are:
 - to implement a class constructor with the args: paddle_pos, goal_side
 - set self.my_display_name with your team's name, max. 15 characters
 - to implement the function next_move(self, current_state),
    returning the next position of your paddle
"""

import copy
import utils

class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "BLAZERS"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 10
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
        # update my paddle pos
        # I need to do this because GameCore moves my paddle randomly
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle2_pos']


        # estimate puck path
        path = estimate_path(current_state, self.future_size)

        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        # find if puck path is inside my interest area
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 1.2


        if self.my_goal == 'left':
            if current_state['goals']['left'] > current_state['goals']['right']:
                roi_radius = current_state['board_shape'][0] * current_state['goal_size']
        else:
            if current_state['goals']['left'] < current_state['goals']['right']:
                roi_radius = current_state['board_shape'][0] * current_state['goal_size']

        pt_in_roi = None
        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break


        # can move and puck behind me
        if pt_in_roi and is_puck_behind(current_state, self.my_goal):
            if self.my_goal == 'left':
                if current_state['puck_pos']['y'] < current_state['board_shape'][0]/2:
                    target_pos = {'x': 0,
                                  'y': self.my_goal_center['y'] - current_state['goal_size']}
                else:
                    target_pos = {'x': 0,
                                  'y': self.my_goal_center['y'] + current_state['goal_size']}
            else:
                if current_state['puck_pos']['y'] < current_state['board_shape'][0]/2:
                    target_pos = {'x': current_state['board_shape'][1],
                                  'y': self.my_goal_center['y'] - current_state['goal_size']}
                else:
                    target_pos = {'x': current_state['board_shape'][1],
                                  'y': self.my_goal_center['y'] + current_state['goal_size']}

            # move to target
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

        # can move and puck on my side
        elif pt_in_roi and search(current_state, self.my_goal):
            #########################################################
            #########################################################
            #Left Side
            #########################################################
            #########################################################
            if self.my_goal == 'left':
                # estimate an aiming position
                # shoot center
                if is_enemy_high(current_state, self.my_goal) or is_enemy_low(current_state, self.my_goal):
                    if is_enemy_high(current_state, self.my_goal):
                        target_point_y = self.opponent_goal_center['y'] - current_state['board_shape'][0]/16 * 3
                    else:
                        target_point_y = self.opponent_goal_center['y'] + current_state['board_shape'][0]/16 * 3
                    self.posN = {'x': self.opponent_goal_center['x'],
                                 'y': target_point_y}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                           self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])


                # shoot high
                elif current_state['paddle2_pos']['y'] < current_state['board_shape'][0]/2:
                    posy = current_state['board_shape'][0] + (current_state['board_shape'][0] - current_state['puck_pos']['y'])
                    m = ((self.opponent_goal_center['y'] + current_state['board_shape'][0]/16 * 3) - posy)/(self.opponent_goal_center['x'] - current_state['puck_pos']['x'])
                    b = posy - (m * current_state['puck_pos']['x'])
                    target_point_x = ((current_state['board_shape'][0] - current_state['puck_radius']) - b)/m
                    self.posN = { 'x':target_point_x,
                                  'y': current_state['board_shape'][0]}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                           self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])

                # shoot low
                else:
                    posy = current_state['puck_pos']['y'] * -1
                    m = ((self.opponent_goal_center['y'] - current_state['board_shape'][0]/16 * 3) - posy)/(self.opponent_goal_center['x'] - current_state['puck_pos']['x'])
                    b = posy - (m * current_state['puck_pos']['x'])
                    target_point_x = (current_state['puck_radius'] - b)/m
                    self.posN = {'x':target_point_x,
                                 'y': 0}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                          self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])

                # move to target
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

            #########################################################
            #########################################################
            #Right Side
            #########################################################
            #########################################################
            else:
                # estimate an aiming position
                # shoot center +/- C
                if  is_enemy_high(current_state, self.my_goal) or is_enemy_low(current_state, self.my_goal):
                    if is_enemy_high(current_state, self.my_goal):
                        target_point_y = self.opponent_goal_center['y'] - current_state['board_shape'][0]/16 * 3
                    else:
                        target_point_y = self.opponent_goal_center['y'] + current_state['board_shape'][0]/16 * 3
                    self.posN = {'x': self.opponent_goal_center['x'],
                                 'y': target_point_y}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                           self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])


                # shoot high
                elif current_state['paddle1_pos']['y'] < current_state['board_shape'][0]/2:
                    posy = current_state['board_shape'][0] + (current_state['board_shape'][0] - current_state['puck_pos']['y'])
                    m = (self.opponent_goal_center['y'] - posy)/(self.opponent_goal_center['x'] - current_state['puck_pos']['x'])
                    b = posy - (m * current_state['puck_pos']['x'])
                    target_point_x = ((current_state['board_shape'][0] - current_state['puck_radius']) - b)/m
                    self.posN = { 'x':target_point_x,
                                  'y': current_state['board_shape'][0]}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                           self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])

                # shoot low
                else:
                    posy = current_state['puck_pos']['y'] * -1
                    m = (self.opponent_goal_center['y'] - posy)/(self.opponent_goal_center['x'] - current_state['puck_pos']['x'])
                    b = posy - (m * current_state['puck_pos']['x'])
                    target_point_x = (current_state['puck_radius'] - b)/m
                    self.posN = {'x':target_point_x,
                                 'y': 0}
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                          self.posN, current_state['puck_radius'],
                                           current_state['paddle_radius'])

                # move to target
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

        # return to center
        else:
            if self.my_goal == 'left':
                target_pos = {'x': current_state['board_shape'][1]/16*3,
                              'y': self.my_goal_center['y']}
            else:
                target_pos = {'x': current_state['board_shape'][1] - current_state['board_shape'][1]/16*3,
                              'y': self.my_goal_center['y']}

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

        # return coordinates
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

def is_enemy_low (current_state, side):
    if side == 'right':
        if current_state['paddle1_pos']['y'] < current_state['board_shape'][0]/4:
            return True
        else:
            return False
    else:
        if current_state['paddle2_pos']['y'] < current_state['board_shape'][0]/4:
            return True
        else:
            return False

def is_enemy_high (current_state, side):
    if side == 'right':
        if current_state['paddle1_pos']['y'] > current_state['board_shape'][0]/4 * 3:
            return True
        else:
            return False
    else:
        if current_state['paddle2_pos']['y'] > current_state['board_shape'][0]/4 * 3:
            return True
        else:
            return False

def search(current_state, side):
    if current_state['puck_speed']['x'] == 0:
        return True
    if side == 'right':
        if current_state['puck_speed']['x'] < -150:
            return False
        else:
            return True
    else:
        if current_state['puck_speed']['x'] > 150:
            return False
        else:
            return True

def is_puck_behind(current_state, side):
    if side == 'right':
        if current_state['puck_pos']['x'] > current_state['paddle2_pos']['x']:
            return True
        else:
            return False
    else:
        if current_state['puck_pos']['x'] < current_state['paddle1_pos']['x']:
            return True
        else:
            return False
