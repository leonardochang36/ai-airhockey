""" GameCore module

This module implements all logic and rules of the challenge.
Also, specify game parameters.

Modify it under your own responsability, for the competition purposes only
the original version will be used.
"""

import random
import copy
import time

import utils

class GameCore:
    def __init__(self, p1, p2, board, init_state, error_rate, gui_core):
        self.player1 = p1
        self.player2 = p2
        self.goal_sides = {'left': p1 if p1.my_goal == 'left' else p2,
                           'right': p1 if p1.my_goal == 'right' else p2}
        self.board = board
        self.state = init_state
        self.error_rate = error_rate
        self.gui_core = gui_core
        self.goals = {'left': 0, 'right': 0}
        self.verbose = False
        self.game_begin_time = time.time()
        self.game_elapsed_ticks = 0
        self.in_initial_state = 0
        self.max_idle_moves = 100    # max number of idle moves after init position
        self.winning_points = 7      # goals to win
        self.max_time = 0.7          # max time (seconds) for one move, i.e., player.next_move
        self.game_max_ticks = 2500   # max ticks (moves) for a game


    def begin_game(self):
        while True:
            self.state['is_goal_move'] = None

            #####################################################################
            ### Check winning conditions
            #####################################################################
            is_stop = self.check_stop_game_conditions()
            if is_stop:
                self.gui_core.release_all()
                return is_stop

            #####################################################################
            ### MOVE puck
            #####################################################################
            self.process_move_from_state()

            # copy state to avoid any modification inside player's logic
            state_copy = copy.copy(self.state)

            #####################################################################
            ### Make Player 1 move
            #####################################################################
            try:
                t0 = time.time()
                self.state['paddle1_pos'] = self.make_player_move(state_copy, self.player1)
                assert time.time() - t0 < self.max_time, ('TIME VIOLATION by: ' +
                                                          self.player1.my_display_name)
            except Exception as exc:
                self.gui_core.release_all()
                return {'status': 'ERROR', 'info': exc,
                        'goals': self.goals, 'winner': self.player2.my_display_name}

            #####################################################################
            ### Make Player 2 move
            #####################################################################
            try:
                t0 = time.time()
                self.state['paddle2_pos'] = self.make_player_move(state_copy, self.player2)
                assert time.time() - t0 < self.max_time, ('TIME VIOLATION by: ' +
                                                            self.player2.my_display_name)
            except Exception as exc:
                self.gui_core.release_all()
                return {'status': 'ERROR', 'info': exc,
                        'goals': self.goals, 'winner': self.player1.my_display_name}

            #####################################################################
            ### Visual feedback
            #####################################################################
            flag = self.resolve_gui()
            if flag:
                return flag

        self.gui_core.release_all()
        return {'status': 'ERROR', 'info': 'Unknown error occurred',
                'goals': self.goals, 'winner': None}


    def check_paddle_valid_move(self, new_pos, previous_pos, state, player):
        # check if is in move range
        max_offset = state['paddle_max_speed'] * state['delta_t'] + 0.000001
        if utils.distance_between_points(new_pos, previous_pos) > max_offset:
            raise ValueError('RULES VIOLATION: paddle moved faster than speed limit for ' +
                             player.my_display_name)

        # check if is inside board limits
        if utils.is_out_of_boundaries_paddle(new_pos, state) is not None:
            raise ValueError('RULES VIOLATION: Paddle moved beyond board limits for ' +
                             player.my_display_name)

        # check if is not inside goal area
        if utils.is_inside_goal_area_paddle(new_pos, state) is True:
            raise ValueError('RULES VIOLATION: Paddle moved inside goal area for ' +
                             player.my_display_name)

        # check if paddle is inside player's area
        if self.goal_sides['left'] is player and new_pos['x'] > \
             self.board.shape[1]/2 - self.state['puck_radius']:
            raise ValueError('RULES VIOLATION: Paddle moved beyond center line for ' +
                             player.my_display_name)
        if self.goal_sides['right'] is player and new_pos['x'] < \
             self.board.shape[1]/2 + self.state['puck_radius']:
            raise ValueError('RULES VIOLATION: Paddle moved beyond center line for ' +
                             player.my_display_name)
        return None


    def make_player_move(self, state, player):
        # get player's move
        paddle_new_pos = player.next_move(state)

        # validate received move
        paddle_pos = 'paddle' + ('1' if self.goal_sides['left'] is player else '2') + '_pos'
        self.check_paddle_valid_move(paddle_new_pos, self.state[paddle_pos], self.state, player)

        # add randomness of self.error rate maximum size and inside the board
        ## horizontal shift
        lower_bound = min(paddle_new_pos['x'] - self.state['paddle_radius'], self.error_rate)
        upper_bound = min(self.state['board_shape'][1] - paddle_new_pos['x'] - self.state['paddle_radius'],
                          self.error_rate)
        paddle_new_pos['x'] += random.uniform(-lower_bound, upper_bound)

        ## vertical shift
        lower_bound = min(paddle_new_pos['y'] - self.state['paddle_radius'], self.error_rate)
        upper_bound = min(self.state['board_shape'][0] - paddle_new_pos['y'] - self.state['paddle_radius'],
                          self.error_rate)
        paddle_new_pos['y'] += random.uniform(-lower_bound, upper_bound)

        # if pos + randomness is inside goal area, move it out this area
        if utils.is_inside_goal_area_paddle(paddle_new_pos, self.state):
            center = {'x': 0 if self.goal_sides['left'] is player else self.board.shape[1],
                      'y': self.board.shape[0]/2}
            r = self.state['goal_size'] * self.board.shape[0] / 2 + 2
            paddle_new_pos = utils.nearest_point_in_circle(center, r, paddle_new_pos)

        return paddle_new_pos


    def set_random_position_at(self, side):
        x_offset = 0.25 if side == 'left' else 0.75

        pos = {'x': self.board.shape[1] * x_offset,
               'y': random.uniform(0 + self.state['puck_radius'],
                                   self.board.shape[0] -
                                   self.state['puck_radius'])}
        return pos


    def check_stop_game_conditions(self):
        # check if any player achieved winning points
        winner = [k for k, v in self.goals.items() if v >= self.winning_points]
        if winner:
            return {'status': 'SUCCESS', 'info': 'Winner by points', 'goals': self.goals,
                    'winner': self.goal_sides[winner[0]].my_display_name}

        # check if game ticks were consumed
        if self.game_elapsed_ticks > self.game_max_ticks:
            # check is game is tied
            # if yes, give extra 30% time
            # if not, declare a winner
            if self.goals['left'] != self.goals['right']:
                winner = max(self.goals, key=(lambda key: self.goals[key]))
                return {'status': 'SUCCESS', 'info': 'Winner by time', 'goals': self.goals,
                        'winner': self.goal_sides[winner].my_display_name}
            elif self.game_elapsed_ticks > self.game_max_ticks * 1.3:
                return {'status': 'SUCCESS', 'info': 'Game tied by time', 'goals': self.goals,
                        'winner': None}

        self.game_elapsed_ticks += 1
        return None


    def process_goal_for(self, goal_for, puck_to=None):
        # update scores
        self.goals[goal_for] += 1
        self.state['goals'] = self.goals
        self.state['is_goal_move'] = goal_for

        # show goal state in video feed
        self.resolve_gui()

        # set new puck position
        if not puck_to:
            puck_to = ('left' if goal_for == 'right' else 'right')
        self.state['puck_pos'] = self.set_random_position_at(puck_to)
        self.state['puck_speed'] = {'x': 0,
                                    'y': utils.vector_l2norm(self.state['puck_speed'])}
        self.in_initial_state = 0

        # set paddles to initial position
        self.state['paddle1_pos'] = {'x': self.board.shape[0]*self.state['goal_size']/2+1,
                                     'y': self.board.shape[0]/2}
        self.state['paddle2_pos'] = {'x': self.board.shape[1] - self.board.shape[0]*self.state['goal_size']/2-1,
                                     'y': self.board.shape[0]/2}
        return


    def process_move_from_state(self):
        new_puck_pos = utils.next_pos_from_state(self.state)

        # after initial position check for idleness
        if self.in_initial_state is not None:
            # if puck position changed, OK
            if new_puck_pos['x'] != self.state['puck_pos']['x']:
                self.in_initial_state = None
            # if number of idle moves exceeded, penalize with goal
            elif self.in_initial_state >= self.max_idle_moves:
                goal_for = 'left' if self.state['puck_pos']['x'] > self.board.shape[1]/2 else 'right'
                self.process_goal_for(goal_for, puck_to=('left' if goal_for == 'left' else 'right'))
                return goal_for
            # if idle but idle moves not exceed, increment counter
            else:
                self.in_initial_state += 1

        # update pos in state
        self.state['puck_pos'] = new_puck_pos

        # if is goal
        if utils.is_goal(self.state) is not None:
            self.process_goal_for(utils.is_goal(self.state))
            return utils.is_goal(self.state)

        # update speed (and direction) in state
        self.state['puck_speed'] = utils.next_speed(self.state)
        return None


    def resolve_gui(self):
        flag = self.gui_core.resolve_gui(self.state, self.player1.my_display_name,
                                         self.player2.my_display_name)
        if flag < 0:
            self.gui_core.release_all()
            return {'status': 'ERROR', 'info': 'Program exited by user (ESC key pressed)',
                    'goals': self.goals, 'winner': None}
        return None
