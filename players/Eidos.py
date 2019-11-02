""" Player module

This is a template/example class for your player.
This is the only file you should modify.

The logic of your hockey robot will be implemented in this class.
Please implement the interface next_move().

The only restrictions here are:
 - to implement a class constructor with the args: paddle_pos, goal_side
 - set self.my_display_name with your team's name, max. 15 characters
 - to implement the function next_move(self, current_state),
    returnin the next position of your paddle
"""

import copy
import utils
import random

class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "Eidos"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 30
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

        #Save the position of the enemy paddle
        enemy_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'right' \
                                                              else current_state['paddle2_pos']

        # estimate puck path
        path = estimate_path(current_state, self.future_size)

        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        y1 = random.uniform(250, 370)
        y2 = random.uniform(140, 250)
        #Targets where our paddle will aim
        attackTarget1 = {'x': current_state['board_shape'][1]*0.7 if self.my_goal=='left' else current_state['board_shape'][1]* 0.3, 'y': 512}
        attackTarget2 = {'x': current_state['board_shape'][1]*0.7 if self.my_goal=='left' else current_state['board_shape'][1]* 0.3, 'y': 0}

        """
        #Shinobi mode
        #new_paddle_pos = {'x': self.my_paddle_pos['x'], 'y': current_state['puck_pos']['y']}
        new_paddle_pos = self.my_paddle_pos
        new_paddle_pos['y'] = current_state['puck_pos']['y']
        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
            utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None and \
            is_inside_area51(new_paddle_pos ,current_state) is False and \
            utils.distance_between_points(current_state['puck_pos'], self.my_paddle_pos) > 50:
            self.my_paddle_pos = new_paddle_pos 
        """

        defenseMode = False
        # find if puck path is inside my interest area
        

        pt_in_roi = None
        for p in path:
            
            if self.my_goal == 'left':
                if current_state['puck_pos']['x'] <= 238.75:
                    roi_radius = current_state['board_shape'][1] * current_state['goal_size']
                    defenseMode = True
                else:
                    roi_radius = current_state['board_shape'][1] * current_state['goal_size'] * 2
            else:
                if current_state['puck_pos']['x'] >= 716.25:
                    roi_radius = current_state['board_shape'][1] * current_state['goal_size']
                    defenseMode = True
                else:
                    roi_radius = current_state['board_shape'][1] * current_state['goal_size'] * 2

            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break
        
        if defenseMode:
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
                
                defenseMode = False


        #If the puck is on the enemy side, our paddle will return to the goal area
        elif (current_state['puck_pos']['x'] > 477.5 and self.my_goal=='left') or (current_state['puck_pos']['x'] < 477.5 and self.my_goal=='right'):
            
            #The target position is the center of the goal area
            if self.my_goal == 'left':
                target_pos = {'x':116.2, 'y': 256}  
            else:
                target_pos = {'x':838.8, 'y': 256}

            # move to target position
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
                # check if computed new position is inside area51
                if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                    utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos

        #If the puck is on our side and the puck is in front of our paddle, the paddle will try to hit it
        elif ((current_state['puck_pos']['x'] >= self.my_paddle_pos['x'] and self.my_goal == 'left') or \
            (current_state['puck_pos']['x'] <= self.my_paddle_pos['x'] and self.my_goal == 'right')):
            
            if pt_in_roi:
                
                if(enemy_paddle_pos['y'] > 256):
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                    attackTarget2, current_state['puck_radius'],
                                    current_state['paddle_radius'])
                else:
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                    attackTarget1, current_state['puck_radius'],
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
                    # check if computed new position is inside area51
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                        utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                        self.my_paddle_pos = new_paddle_pos
            

        #If the puck is behind the paddle, the paddle avoids the puck to avoid comitting an autogoal
        elif current_state['puck_pos']['x'] < self.my_paddle_pos['x']:

            # move to target position, taking into account the max. paddle speed
    
            direction_vector = {'x': current_state['puck_pos']['x'] - self.my_paddle_pos['x'],
                                'y': current_state['puck_pos']['y'] - self.my_paddle_pos['y']}
            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                for k, v in direction_vector.items()}

            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                utils.distance_between_points(current_state['puck_pos'], self.my_paddle_pos))

            direction_vector = {k: v * - movement_dist
                                for k, v in direction_vector.items()}
            new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                'y': self.my_paddle_pos['y'] + direction_vector['y']}

            new_paddle_pos = utils.rectify_circle_out_of_bounds(new_paddle_pos, self.my_goal, current_state)

            # check if computed new position in not inside goal area
            # check if computed new position in inside board limits
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                self.my_paddle_pos = new_paddle_pos
        
        #Return the new position for the paddle
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

def is_inside_area51(paddle_pos, state):

    if utils.next_pos_from_state(state)['x'] + state['puck_radius'] <= state['board_shape'][1] * 0.150:
        return True

    return False