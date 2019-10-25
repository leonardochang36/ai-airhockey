import copy
import utils
import cv2 as cv
import numpy as np
import time

class Player:
    def __init__(self, paddle_pos, goal_side):
        self.future_size = 30
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos
        self.my_display_name = "DREAM TEAM"


    def next_move(self, current_state):
        # estimate puck path
        path = estimate_path(current_state, self.future_size)
        # im = np.zeros(current_state['board_shape'])
        # for p in path:
        #     cv.circle(im, utils.round_point_as_tuple(p[0]), 3, (255,0,0), -1)
        # cv.imshow('a', im)
        # cv.waitKey(10)

        # computing both goal centers
        # this could be moved to the constructor
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        # find if puck path is near my goal
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
        pt_in_roi = None
        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break

        if pt_in_roi:
            #
            target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                        self.opponent_goal_center, current_state['puck_radius'],
                                        current_state['paddle_radius'])

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
                
                # check if computed new position in inside board limits
                if utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos

        # time.sleep(2)
        # return {'x': -12, 'y': -6543}
        return self.my_paddle_pos
        


def estimate_path(current_state, after_time):
    state = copy.copy(current_state)
    path = []
    while after_time > 0:
        state['puck_pos'] = utils.next_pos_from_state(state)
        if utils.is_goal(state) is not None:
            break
        if utils.next_after_boundaries(state):
            state['puck_speed'] = utils.next_after_boundaries(state)
        # state['puck_speed'] = utils.next_speed(state)
        path.append((state['puck_pos'], state['puck_speed']))
        after_time -= state['delta_t']
    return path
