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
        self.my_display_name = "GEC"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 20
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
        -------------------------other----------------------------------
        """

        # update my paddle pos
        # I need to do this because GameCore moves my paddle randomly
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle2_pos']

        self.their_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle1_pos']



        # estimate puck path
        path = estimate_path(current_state, self.future_size)

        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        y = random.uniform(140, 370)
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': y}

        # computing my area center

        self.my_area_center = {'x': current_state['board_shape'][1]/4 if self.my_goal == 'left' else  current_state['board_shape'][1]/4 * 3,
                               'y': current_state['board_shape'][0]/2}


        # computing frontlines

        self.my_frontline = {'x': current_state['board_shape'][1]/8 * 3 if self.my_goal == 'left' else  current_state['board_shape'][1]/8 * 5,
                               'y': current_state['board_shape'][0]/2}


        self.their_frontline = {'x': current_state['board_shape'][1]/8 * 5 if self.my_goal == 'left' else  current_state['board_shape'][1]/8 *3,                              'y': current_state['board_shape'][0]/2}


        
        # computing backlines

        self.my_backline = {'x': current_state['board_shape'][1]/8 if self.my_goal == 'left' else  current_state['board_shape'][1]/8 * 7,
                               'y': current_state['board_shape'][0]/2}


        self.their_backline = {'x': current_state['board_shape'][1]/8 * 7 if self.my_goal == 'left' else  current_state['board_shape'][1]/8,
                               'y': current_state['board_shape'][0]/2}



        # find if puck path is inside my interest area
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 1.2
        personal_space = current_state['paddle_radius'] * 3
        defensive_point = None
        offensive_point = None
        coming = False
        prevd = None
        behind = False
        
        for p in path:
            if utils.distance_between_points(current_state['puck_pos'], self.my_paddle_pos) < personal_space: 
                offensive_point = p
                break

        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                defensive_point = p
                break

        for p in path:
            if prevd != None:
                
                if utils.distance_between_points(p[0], self.my_goal_center) < prevd:

                    coming = True

            prevd = utils.distance_between_points(p[0], self.my_goal_center)

        if self.my_goal == 'left':
            if (current_state['puck_pos']['x'] < self.my_paddle_pos['x']):
                behind = True
        else:
            if (current_state['puck_pos']['x'] > self.my_paddle_pos['x']):
                behind = True

        '''
        -------------------------movement----------------------------------
        '''

        def indirect_goal_center (current_state):
            #find ideal xpos
            smallest_dist = 9999
            bounce_points = [0,125,249,373,497,621,745,869,995]
            behinderino = False
            xpos = 497

            if self.my_goal == 'left':
                if (current_state['puck_pos']['x'] < self.my_paddle_pos['x']):
                    behinderino = True
            else:
                if (current_state['puck_pos']['x'] > self.my_paddle_pos['x']):
                    behinderino = True


            if not behinderino:
                xpos = self.their_backline['x']


            if self.their_paddle_pos['y'] < (current_state['board_shape'][0] / 2):
                poss = {'x': xpos, 'y': current_state['board_shape'][0]} 
            else:
                poss = {'x': xpos, 'y': 0} 
            return poss  

        def NME_IN_PATH (target_pos):
            if (target_pos['y'] - self.their_paddle_pos['y']) < current_state['paddle_radius'] * 2:
                return True
            else:
                return False


        def target_to_position(target_pos):
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
                else:
                    target_to_position(self.my_area_center)
            
            return  self.my_paddle_pos


        """
        ----------------------------------engagement scenarios -------------------------------------
        """

        if behind and defensive_point:
            goalerino = indirect_goal_center(current_state)
            target_pos = utils.aim(defensive_point[0], defensive_point[1],goalerino , current_state['puck_radius'], current_state['paddle_radius'])
            return target_to_position(target_pos)
        elif behind and offensive_point:
            goalerino = {'x': self.my_goal_center['x'] , 'y': 0 }
            target_pos = utils.aim(offensive_point[0], offensive_point[1],goalerino , current_state['puck_radius'], current_state['paddle_radius'])
            return target_to_position(target_pos)


        elif defensive_point:
            # estimate an aiming position

            target_pos = utils.aim(defensive_point[0], defensive_point[1],
                                   self.opponent_goal_center, current_state['puck_radius'],
                                   current_state['paddle_radius'])

            if NME_IN_PATH(target_pos):
                target_pos = utils.aim(defensive_point[0], defensive_point[1],
                                   indirect_goal_center(current_state), current_state['puck_radius'],
                                   current_state['paddle_radius'])
                return target_to_position(target_pos)
            else: 
                return target_to_position(target_pos)

        elif offensive_point: 
            # estimate an aiming position
            
            target_pos = utils.aim(offensive_point[0], offensive_point[1],
                                   self.opponent_goal_center, current_state['puck_radius'],
                                   current_state['paddle_radius'])

            if NME_IN_PATH(target_pos):
                target_pos = utils.aim(offensive_point[0], offensive_point[1],
                                   indirect_goal_center(current_state), current_state['puck_radius'],
                                   current_state['paddle_radius'])
                return target_to_position(target_pos)
            else: 
                return target_to_position(target_pos)


        elif coming: #idle defensive
           
             
            target_pos = line_intersection(self.their_paddle_pos['x'],self.their_paddle_pos['y'],current_state['puck_pos']['x'], current_state['puck_pos']['y'],self.my_backline['x'], current_state['board_shape'][0], self.my_frontline['x'],0 )

            return target_to_position(target_pos)

        
        else: #idle offensive
           
            target_pos = line_intersection(self.their_paddle_pos['x'],self.their_paddle_pos['y'],current_state['puck_pos']['x'], current_state['puck_pos']['y'],self.my_frontline['x'], current_state['board_shape'][0], self.my_frontline['x'],0 )
            

            return target_to_position(target_pos)


        print("HUH")
        return target_to_position(self.my_area_center)


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

def estimate_path_bounce(current_state, after_time):
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

def line_intersection(x1,y1,x2,y2,x3,y3,x4,y4):
    px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ) 
    py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
    linerino = {'x': px , 'y': py }
    return linerino


