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
        self.my_display_name = "Leonardo DaVinChang"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 15
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos
        self.initial_pos = {'x': paddle_pos['x'] + 1, 'y': paddle_pos['y']}
        self.new_initial_pos = {'x': paddle_pos['x'] + 1, 'y': paddle_pos['y']}
        

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

        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
                               
        enemy_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}

        path = []
        path = estimate_path(current_state, self.future_size)
        target = self.initial_pos

        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 1.2
        pt_in_roi = None
        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break
        
        if self.my_goal == 'left':
            #enemy goals grater than us
            if current_state['goals']['right'] >= current_state['goals']['left']:
                self.new_initial_pos = {'x': self.initial_pos['x'] + 30, 'y':self.initial_pos['y']}
            else:
                self.new_initial_pos = self.initial_pos
            #if the puck is in the right field, the paddle defends
            if is_puck_right(current_state):
                # get the target position for the paddle
                target = self.new_initial_pos

            else: 
                if  current_state['puck_speed']['x'] <= 50:
                    if is_puck_behind(self.my_paddle_pos, current_state) == False:
                        my_enemy_puck_pos_quarter = enemy_puck_pos_quarter(self.my_goal, current_state)
                        #if the enemy is at the center of the field vertically
                        if my_enemy_puck_pos_quarter == 2:
                            target_shot = get_target_shot(enemy_goal_center, self.my_goal_center, current_state)
                            #print(target_shot)
                            if pt_in_roi:
                                target = utils.aim(pt_in_roi[0], pt_in_roi[1], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius']) 
                            else:
                                target = utils.aim(current_state['puck_pos'], current_state['puck_speed'], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius'])
                        else:
                            target_shot = get_target_shot_quarter(enemy_goal_center, self.my_goal, current_state)
                            if pt_in_roi:
                                target = utils.aim(pt_in_roi[0], pt_in_roi[1], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius']) 
                            else:
                                target = utils.aim(current_state['puck_pos'], current_state['puck_speed'], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius']) 
                    else:
                        defense_pos = get_defense_pos(self.my_paddle_pos, current_state)
                        target = defense_pos


                else:
                    target = self.new_initial_pos
            
            # 
            if target['x'] < (current_state['board_shape'][1] / 2):
                self.my_paddle_pos = next_move_paddle(self.my_paddle_pos, target, current_state)

        else:
            #enemy goals grater than us
            if current_state['goals']['left'] >= current_state['goals']['right']:
                self.new_initial_pos = {'x': self.initial_pos['x'] - 30, 'y':self.initial_pos['y']}
            else:
                self.new_initial_pos = self.initial_pos
            if is_puck_left(current_state):
                # get the target position for the paddle
                target = self.new_initial_pos

            else: 
                if  current_state['puck_speed']['x'] >= (-50):
                    if is_puck_behind_right(self.my_paddle_pos, current_state) == False:
                        my_enemy_puck_pos_quarter = enemy_puck_pos_quarter(self.my_goal, current_state)
                        #if the enemy is at the center of the field vertically
                        if my_enemy_puck_pos_quarter == 2:
                            target_shot = get_target_shot(enemy_goal_center, self.my_goal_center, current_state)
                            #print(target_shot)
                            if pt_in_roi:
                                target = utils.aim(pt_in_roi[0], pt_in_roi[1], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius']) 
                            else:
                                target = utils.aim(current_state['puck_pos'], current_state['puck_speed'], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                current_state['paddle_radius'])
                        else:
                            target_shot = get_target_shot_quarter(enemy_goal_center, self.my_goal, current_state)
                            if pt_in_roi:
                                target = utils.aim(pt_in_roi[0], pt_in_roi[1], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius']) 
                            else:
                                target = utils.aim(current_state['puck_pos'], current_state['puck_speed'], {'x': target_shot['x'], 'y': target_shot['y']}, current_state['puck_radius'],
                                                    current_state['paddle_radius'])
                    else:
                        defense_pos = get_defense_pos_right(self.my_paddle_pos, current_state)
                        target = defense_pos
                else:
                    target = self.new_initial_pos
            
            # 
            if target['x'] > (current_state['board_shape'][1] / 2):
                self.my_paddle_pos = next_move_paddle(self.my_paddle_pos, target, current_state)

        return self.my_paddle_pos

def get_defense_pos(paddle_pos, current_state):
    if is_puck_top(current_state):
        defense_pos = {'x': paddle_pos['x'] - 10, 'y': paddle_pos['y']}
    else:
        defense_pos = {'x': paddle_pos['x'] - 10, 'y': paddle_pos['y']}
    return defense_pos

def get_defense_pos_right(paddle_pos, current_state):
    if is_puck_top(current_state):
        defense_pos = {'x': paddle_pos['x'] + 10, 'y': paddle_pos['y']}
    else:
        defense_pos = {'x': paddle_pos['x'] + 10, 'y': paddle_pos['y']}
    return defense_pos

def get_target_shot_quarter(enemy_goal_center, my_goal, current_state):
    enemy_pos = enemy_puck_pos_quarter(my_goal, current_state)
    #the target x is 512
    if my_goal == 'left':
        #shoot down the enemy to the goal edge
        if enemy_pos == 0:
            x1 = current_state['board_shape'][1]
            y1 = current_state['board_shape'][0]/2 + ((current_state['board_shape'][0] * current_state['goal_size'])/2)
        else:
            x1 = current_state['board_shape'][1]
            y1 = y1 = current_state['board_shape'][0]/2 - ((current_state['board_shape'][0] * current_state['goal_size'])/2)
    else:
        if enemy_pos == 0:
            x1 = 0
            y1 = current_state['board_shape'][0]/2 + ((current_state['board_shape'][0] * current_state['goal_size'])/2)
        else:
            x1 = 0
            y1 = y1 = current_state['board_shape'][0]/2 - ((current_state['board_shape'][0] * current_state['goal_size'])/2)
    
    target_shot = {'x': x1, 'y':y1}
    return target_shot

def get_target_shot(enemy_goal_center, my_goal, current_state):
    """
        Function that computes the target of the next shot, taking in cosideration the position of the enemy paddle to shot in the other side vertically
        using the formula of the pendent of the two points: 1. the puck position times 2, 2. the enemy goal center

        args:
            enemy_goal_center
            current_state
        return:
                the target of the next shot
            target_shot = {'x': target_shot_x, 'y':target_shot_y}
    """

    enemy_pos = enemy_puck_pos(my_goal, current_state)
    #shoot down the enemy
    if enemy_pos == 0:
        dif = current_state['board_shape'][0] - current_state['puck_pos']['y']
        x1 = current_state['puck_pos']['x']
        y1 = current_state['board_shape'][0] + dif
        y2 = current_state['board_shape'][0]/2 + (((current_state['board_shape'][0] * current_state['goal_size'])/2))
    else:
        x1 = current_state['puck_pos']['x']
        y1 = 0 - current_state['puck_pos']['y']
        y2 = current_state['board_shape'][0]/2 - (((current_state['board_shape'][0] * current_state['goal_size'])/2))

    x2 = enemy_goal_center['x']

    m = (y2 - y1)/(x2 - x1)

    b = y1 - (m * x1)
    
    if enemy_pos == 0:
        target_shot_x = (current_state['board_shape'][0] - b) / m
        target_shot_y = current_state['board_shape'][0]
    else:
        target_shot_x = (0 - b) / m
        target_shot_y = 0
    
    target_shot = {'x': target_shot_x, 'y':target_shot_y}

    return target_shot

def is_puck_behind(paddle_pos, current_state):
    if paddle_pos['x'] > current_state['puck_pos']['x']:
        return True
    return False

def is_puck_behind_right(paddle_pos, current_state):
    if paddle_pos['x'] < current_state['puck_pos']['x']:
        return True
    return False

def enemy_puck_pos_quarter(my_goal, current_state):
    if my_goal == 'left':
        if current_state['paddle2_pos']['y'] < current_state['board_shape'][0]/4:
            return 0
        elif current_state['paddle2_pos']['y'] > current_state['board_shape'][0]/4*3:
            return 1
    else: 
        if current_state['paddle1_pos']['y'] < current_state['board_shape'][0]/4:
            return 0
        elif current_state['paddle1_pos']['y'] > current_state['board_shape'][0]/4*3:
            return 1
    return 2

def enemy_puck_pos(my_goal, current_state):
    """
        args:
            my_goal: if the paddle is on the left or right side
        return:
            0: if is in the first second of the field
            1: if is in the second second of the field
    """
    if my_goal == 'left':
        if current_state['paddle2_pos']['y'] < current_state['board_shape'][0]/2:
            return 0
        elif current_state['paddle2_pos']['y'] >= current_state['board_shape'][0]/2:
            return 1
    else: 
        if current_state['paddle1_pos']['y'] < current_state['board_shape'][0]/2:
            return 0
        elif current_state['paddle1_pos']['y'] >= current_state['board_shape'][0]/2:
            return 1
    return 1

def is_puck_top(current_state):
    """
        Args: 
            current_state, to obtain the position of the puck

        Return:
            true if the position of the puck is on the top side of the board
    """
    if current_state['puck_pos']['y'] < current_state['board_shape'][0]/2:
        return False
    return True

def is_puck_right(current_state):
    """
        Args: 
            current_state, to obtain the position of the puck

        Return:
            true if the position of the puck is on the right side of the board
    """
    if current_state['puck_pos']['x'] > (current_state['board_shape'][1]/2*3 ):
        return True
    return False

def is_puck_left(current_state):
    """
        Args: 
            current_state, to obtain the position of the puck

        Return:
            true if the position of the puck is on the right side of the board
    """
    if current_state['puck_pos']['x'] < (current_state['board_shape'][1]/3 ):
        return True
    return False

def next_move_paddle(paddle_pos, target_pos, current_state):
    """
        Args:
            paddle_pos:
            target_pos:

        Return:
            the next movement of the paddle of 1 frame x and y
            next_move
    """
    if target_pos != paddle_pos:
        direction_vector = {'x': target_pos['x'] - paddle_pos['x'],
                            'y': target_pos['y'] - paddle_pos['y']}
        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                            for k, v in direction_vector.items()}

        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                            utils.distance_between_points(target_pos, paddle_pos))
        direction_vector = {k: v * movement_dist
                            for k, v in direction_vector.items()}
        next_move = {'x': paddle_pos['x'] + direction_vector['x'],
                            'y': paddle_pos['y'] + direction_vector['y']}

    # check if computed new position in not inside goal area
    # check if computed new position in inside board limits
    if utils.is_inside_goal_area_paddle(next_move, current_state) is False and \
            utils.is_out_of_boundaries_paddle(next_move, current_state) is None:
        return next_move
        
    return paddle_pos
    
    
    """
    if paddle_pos[]
    next_move = {'x':paddle_pos['x'] + 5, 'y':paddle_pos['y'] + 5}
    return next_move
    """


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
