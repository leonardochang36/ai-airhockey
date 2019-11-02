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
import json

import random, math

import numpy as np
from numpy import ones,vstack
from numpy.linalg import lstsq


class Player:
    def __init__(self, paddle_pos, goal_side):

        # Name
        self.my_display_name = "Lobo"
        self.my_goal = goal_side
        self.my_paddle_pos = paddle_pos
        self.start = True
        self.my_goal_center = {}
        self.pos_x = 0

        self.mul = 0

        if goal_side == 'left': 
            self.mul = 1
            self.pos_x = 120 
        else: 
            self.pos_x = 870
            self.mul = -1


    def next_move(self, current_state):

        target_pos = {'x':0, 'y': 0}

        if self.my_goal == 'left':
            self.my_paddle_pos = current_state['paddle1_pos']
        else:
            self.my_paddle_pos = current_state['paddle2_pos']

        path = estimate_path(current_state, 3)

        if len(path) > 2:
            direc = getDirection(path[0][0], path[2][0]) 
        else:
            direc = {'x':0, 'y':0}

        if get_side_puck(self.my_goal, current_state['puck_pos']) and direc['x'] == 0: # Starts in my side
            
            x = current_state['puck_pos']['x'] - 30 * self.mul
            y = 256
            target_pos={'x': x, 'y': y}
        
        elif (self.my_goal == 'left' and direc['x'] < 0) or (self.my_goal == 'right' and direc['x'] > 0):
            x = self.pos_x
            m, c = getEqu(path[0][0], path[2][0])

            y = x*m +c 

            if y < 0 and y > -450: 
                y *= -1
            elif y > 480 and y < 480*2:
                y = 512 - (y - 512)



            if (current_state['paddle2_pos']['y'] < 256) and y > 47 and y < 479:
                y -= 15
            elif (current_state['paddle2_pos']['y'] > 256) and y < 479 and y > 47:
                y += 15

            if y < 32 : y = 32
            elif y >= 480: y = 479

            target_pos={'x': x, 'y': y}

        else:
            x = self.pos_x
            if current_state['puck_pos']['y'] > 256:
                y = 280
            elif current_state['puck_pos']['y'] < 256:
                y = 232
            elif current_state['puck_pos']['y'] == 256:
                y = 256
            target_pos={'x': x, 'y': y}
            
        
        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                            'y': target_pos['y'] - self.my_paddle_pos['y']}
        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                            for k, v in direction_vector.items()}

        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                            utils.distance_between_points(target_pos, self.my_paddle_pos))
        direction_vector = {k: v * movement_dist
                            for k, v in direction_vector.items()}

        self.my_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                            'y': self.my_paddle_pos['y'] + direction_vector['y']}
            
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}

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

def getEqu(a, b):
    points = [(a['x'], a['y']), (b['x'], b['y'])]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords,ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=None)[0]

    return m, c


def getDirection(a, b):

    x = b['x'] - a['x']
    y = b['y'] - a['y']

    direc = {'x': x, 'y': y}
    return direc

def get_side_puck(my_side, puck_pos):

    if my_side == 'left' and puck_pos['x'] < 497.5:
        return True
    elif my_side == 'left' and puck_pos['x'] > 497.5:
        return False
    elif my_side == 'right' and puck_pos['x'] > 497.7: 
        return True
    else: 
        return False

def inside_goal(paddle_pos, center):

    if (paddle_pos['x'] - center['x'])**2 + (paddle_pos['y'] - center['y'])**2 < 116.1**2:
        return True
    else:
        return False