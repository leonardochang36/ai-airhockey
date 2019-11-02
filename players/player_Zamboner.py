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
# Board shape(512, 995, 3)
import copy
import utils
import random


class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "Zamboner"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 30
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos

        # extra
        self.current_state = None
        self.opponent_goal = 'left' if self.my_goal == 'right' else 'right'

    def next_move(self, current_state):
        """ Function that computes the next move of your paddle
        Implement your algorithm here. This will be the only function
        used by the GameCore. Be aware of abiding all the game rules.
        Returns:
            dict: coordinates of next position of your paddle.
        """

        self.current_state = current_state
        # update my paddle pos
        # I need to do this because GameCore moves my paddle randomly, epsilon
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
            else current_state['paddle2_pos']

        # estimate puck path
        path, goal = self.estimate_path()

        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        # puck behind 
        if self.my_goal == "right":
            if current_state['puck_speed']['x'] <= 0 and current_state['puck_pos']['x'] > self.my_paddle_pos['x']: # going left
                target_pos = copy.copy(self.my_paddle_pos)
                target_pos['x'] = current_state['board_shape'][1]/4 + current_state['paddle_radius']
                return self.go_Pos(current_state, target_pos)
            
            if current_state['puck_speed']['x'] <= 0:
                if current_state['puck_pos']['x'] < current_state['board_shape'][1]/2 :#his side 
                    return self.take_position(current_state)

                if self.bounce(current_state,path): # bouncing
                    return self.chang_attack(current_state, path)
                return self.take_position(current_state)
            
        else:   #left
            if current_state['puck_speed']['x'] >= 0 and current_state['puck_pos']['x'] < self.my_paddle_pos['x']: # going right puck
                #go right
                target_pos = copy.copy(self.my_paddle_pos)
                target_pos['x'] = current_state['board_shape'][1]/4 - current_state['paddle_radius']
                return self.go_Pos(current_state, target_pos)
            
            if current_state['puck_speed']['x'] >= 0:
                if current_state['puck_pos']['x'] > current_state['board_shape'][1]/2 :#his side 
                    return self.take_position(current_state)

                if self.bounce(current_state,path):
                    return self.chang_attack(current_state, path)
                return self.take_position(current_state)
            

        return self.chang_attack(current_state, path)
 
        '''
        +       if not self.danger(goal):
            return self.chang_attack(current_state, path)
        else:
            return self.take_position(current_state)
        if current_state['puck_speed']['x'] >= 0:
            return self.chang_attack(current_state, path)
        else:
            return self.take_position(current_state)
        '''
        # Attack if we can. all possible paths without taking enemy pos into account
        candidates = self.attack_candidates(path)
        if candidates:
            # take enemy pos into account
            return self.optimal_attack(candidates)

        # Take position if we're safe. puck not incoming to our goal
        if not self.danger(goal):
            return self.take_position(current_state)

        # Defend because we're in danger.
        candidates = self.defend_candidates(path)
        if candidates:
            return self.optimal_defence(candidates)

        # We're fucked, but might as well take position.
        return self.take_position(current_state)

    def attack_candidates(self, trajectory):
        """Calculates reachable paddle positions where the puck can be hit in a trajectory towards the opposite goal.
        Returns: list of tuples of attack paddle positions and their respective first move"""
        # TODO
        return []

    def optimal_attack(self, candidates):
        """Returns the new position of our paddle where it makes contact with the puck, to start the most optimal attack."""
        # TODO
        #Two options:
        #   Based on our position (if we can get to the shot)
        #   Based on enemy position(if its basically undefendable)
        return {}

    def danger(self, goal):
        """Return whether the puck is bound to reach our goal."""
        return goal == self.opponent_goal

    def defend_candidates(self, trajectory):
        """Lists all reachable paddle position where the puck can be hit so that the new trajectory evades our goal."""
        # TODO
        return []

    def optimal_defence(self, candidates):
        """Returns the first move of the most optimal defence candidate."""
        # TODO
        return {}

    def bounce(self, current_state, path):
        pastPath = None
        for p in path:
            if pastPath:
                if abs(pastPath[0]['x'] - p[0]['x']) < 6:
                    if utils.is_inside_goal_area_paddle(p[0], current_state) is False and utils.is_out_of_boundaries_paddle(p[0], current_state) is None:
                        return True
                # paths repeating, bounce  horizontal, TODO fine tune
                if abs(pastPath[0]['y'] - p[0]['y']) < 6:
                    if utils.is_inside_goal_area_paddle(p[0], current_state) is False and utils.is_out_of_boundaries_paddle(p[0], current_state) is None:
                        return True
            pastPath = p
        return False

    def chang_attack(self, current_state, path):
        # CHANG attack
        # find if puck path is inside my interest area
        goalActualSize = current_state['board_shape'][0] * current_state['goal_size'] 
        pt_in_roi = None
        pastPath = None
        for p in path:
            if pastPath:
                # paths repeating, bounce walls vertically, TODO fine tune
                if abs(pastPath[0]['x'] - p[0]['x']) < 6:
                    if utils.is_inside_goal_area_paddle(p[0], current_state) is False and utils.is_out_of_boundaries_paddle(p[0], current_state) is None:
                        pt_in_roi = p
                        break
                # paths repeating, bounce  horizontal, TODO fine tune
                if abs(pastPath[0]['y'] - p[0]['y']) < 6:
                    if utils.is_inside_goal_area_paddle(p[0], current_state) is False and utils.is_out_of_boundaries_paddle(p[0], current_state) is None:
                        pt_in_roi = p
                        pt_in_roi[0]['y'] += current_state['puck_radius']
                        break

            # if future coordinate path is inside our goal
            if utils.distance_between_points(p[0], self.my_goal_center) < goalActualSize:
                pt_in_roi = p
                break
            pastPath = p

        if pt_in_roi:
            # estimate an aiming position
            vertical_unit = current_state['board_shape'][0]/4
            choice = random.randint(0,2)
            if current_state['paddle2_pos']['y'] < vertical_unit or current_state['paddle2_pos']['y'] > vertical_unit*3 :
                target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                       self.opponent_goal_center, current_state['puck_radius'],
                                       current_state['paddle_radius'])
                #print('CENTER SHOT')
            elif current_state['paddle2_pos']['y'] > vertical_unit*2:
                target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                        self.aim_bounce(pt_in_roi[0], self.opponent_goal_center,current_state['puck_radius'],0 ),
                                        current_state['puck_radius'],
                                        current_state['paddle_radius'])
                #print('Top SHOT')
            else:
                target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                        self.aim_bounce(pt_in_roi[0], self.opponent_goal_center,current_state['puck_radius'],current_state['board_shape'][0] ),
                                        current_state['puck_radius'],
                                        current_state['paddle_radius']) 
               # print('Bot SHOT')                       
            return self.go_Pos(current_state, target_pos)

        return self.my_paddle_pos  # no chang attacks found

    def go_Pos(self, current_state, target_pos):
        if target_pos != self.my_paddle_pos:  # check if im already in the desired area
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
                # Middle line
                if self.my_goal == "right":
                    if new_paddle_pos['x'] > current_state['board_shape'][1]/2 + current_state['paddle_radius']:
                        self.my_paddle_pos = new_paddle_pos
                else:  # left
                    if new_paddle_pos['x'] < current_state['board_shape'][1]/2 - current_state['paddle_radius']:
                        self.my_paddle_pos = new_paddle_pos
        return self.my_paddle_pos

    def take_position(self, current_state):
        """Returns the next position to take, to approach the center of our side of the board"""
        # Set target position to starting position, take into account side of the board necessary
        lt = {'x': current_state['board_shape'][0] *
              current_state['goal_size']/2+1, 'y': current_state['puck_pos']['y']}
        rt = {'x': current_state['board_shape'][1] - current_state['board_shape'][0]
              * current_state['goal_size']/2-1, 'y': current_state['puck_pos']['y']}
        target_pos = lt if self.my_goal == 'left' else rt

        return self.go_Pos(current_state, target_pos)

    def estimate_path(self):
        """ Function that function estimates the next moves in a after_time window
        Returns:
            list: coordinates and speed of puck for next ticks
        """

        state = copy.copy(self.current_state)
        after_time = self.future_size
        path = []
        goal = None
        while after_time > 0:
            state['puck_pos'] = utils.next_pos_from_state(state)
            goal = utils.is_goal(state)
            if goal is not None:
                break
            if utils.next_after_boundaries(state):
                state['puck_speed'] = utils.next_after_boundaries(state)
            path.append((state['puck_pos'], state['puck_speed']))
            after_time -= state['delta_t']
        return path, goal

    def aim_bounce(self, pos, B, puck_radius, border_target = 0):
        """
        args:
            puck position:(A)
            goal_target:(B)
            border_target: (top or bottom coordinate in y(0 or max))

        Returns:
            Desired puck position for a bounce attack(C)
        """
        #Calculate point D
        D_pos = {}
        if(border_target == 0):
            D_pos['x'] = pos['x']
            D_pos['y'] = (border_target + puck_radius) - pos['y']
        else:
            D_pos['x'] = pos['x']
            D_pos['y'] = (border_target - puck_radius) + pos['y']
        
        #Create slope and intersect for the line from B to D
        m = (B['y'] - D_pos['y']) / (B['x'] - D_pos['x'])
        #b = (B['x'] * D_pos['y'] - B['y'] * D_pos['x']) / (B['x'] - D_pos['x'])
        b = D_pos['y'] - m * D_pos['x']
        #Check interect where y = border_target['y'] +- puck_radius
        x_coord = None
        y_coord = None
        if(border_target == 0):
            x_coord = -b / m 
            y_coord = 0
        else:
            x_coord = (border_target-b) / m
            y_coord = border_target
        return {'x':x_coord,'y':y_coord}


'''
        lt = {'x': current_state['board_shape'][0] * current_state['goal_size']/2+1, 'y': current_state['puck_pos']['y']} 
        rt = {'x': current_state['board_shape'][1] - current_state['board_shape'][0]*current_state['goal_size']/2-1,'y': current_state['puck_pos']['y']}
        target_pos = lt if self.my_goal == 'left' else rt
'''
