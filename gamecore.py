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
        self.max_time = 1
        self.verbose = True
        self.in_initial_state = 0
        self.max_idle_moves = 100
        self.winning_points = 700
        self.game_begin_time = time.time()
        self.game_max_time = 60


    def begin_game(self):
        while True:
            #####################################################################
            ### Check winning conditions
            #####################################################################
            if self.check_stop_game_conditions():
                return self.check_stop_game_conditions()
            
            #####################################################################
            ### MOVE puck
            #####################################################################
            new_puck_pos = utils.next_pos_from_state(self.state)
            # 
            if self.in_initial_state is not None:
                if new_puck_pos['x'] != self.state['puck_pos']['x']:
                    self.in_initial_state = None
                elif self.in_initial_state >= self.max_idle_moves:
                    goal_in = 'left' if self.state['puck_pos']['x'] < self.board.shape[1]/2 else 'right'
                    self.goals[goal_in] += 1

                    # set new puck position
                    new_puck_pos_in = 'right' if goal_in == 'left' else 'left'
                    self.state['puck_pos'] = self.set_random_position_at(new_puck_pos_in)
                    self.state['puck_speed'] = {'x': 0,
                                                'y': utils.vector_l2norm(self.state['puck_speed'])}
                    self.in_initial_state = 0
                    continue
                else:
                    self.in_initial_state += 1                    

            self.state['puck_pos'] = new_puck_pos

            # if is goal
            if utils.is_goal(self.state) is not None:
                # update scores
                self.goals[utils.is_goal(self.state)] += 1

                if self.verbose:
                    print('GOAL!!! in', utils.is_goal(self.state), 'the score is', self.goals)

                # set new puck position
                self.state['puck_pos'] = self.set_random_position_at(utils.is_goal(self.state))
                self.state['puck_speed'] = {'x': 0,
                                            'y': utils.vector_l2norm(self.state['puck_speed'])}

            self.state['puck_speed'] = utils.next_speed(self.state)

            # copy state to avoid any modification inside player's logic
            state_copy = copy.copy(self.state)

            #####################################################################
            ### Make Player 1 move
            #####################################################################
            try:
                t0 = time.time()
                self.state['paddle1_pos'] = self.make_player_move(state_copy, self.player1,
                                                                'PLAYER 1')
                assert time.time() - t0 < self.max_time, ('TIME VIOLATION by: ' +
                                                        self.player1.my_display_name)
            except Exception as exc:
                return {'status': 'ERROR', 'info': exc,
                        'goals': self.goals, 'winner': self.player2.my_display_name}

            #####################################################################
            ### Make Player 2 move
            #####################################################################
            try:
                t0 = time.time()
                self.state['paddle2_pos'] = self.make_player_move(state_copy, self.player2,
                                                                    'PLAYER 2')
                assert time.time() - t0 < self.max_time, ('TIME VIOLATION by: ' +
                                                            self.player1.my_display_name)
            except Exception as exc:
                return {'status': 'ERROR', 'info': exc,
                        'goals': self.goals, 'winner': self.player1.my_display_name}

            #####################################################################
            ### Visual feedback
            #####################################################################
            flag = self.gui_core.resolve_gui(self.state)
            if flag < 0:
                self.gui_core.release_all()
                return {'status': 'ERROR', 'info': 'Program exited by user (ESC key pressed)',
                        'goals': self.goals, 'winner': None}

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

        # check if paddle is inside player's area
        if self.goal_sides['left'] is player and new_pos['x'] > self.board.shape[1]/2:
            raise ValueError('RULES VIOLATION: Paddle moved beyond center line for ' +
                             player.my_display_name)
        if self.goal_sides['right'] is player and new_pos['x'] < self.board.shape[1]/2:
            raise ValueError('RULES VIOLATION: Paddle moved beyond center line for ' +
                             player.my_display_name)

        return None


    def make_player_move(self, state, player, player_name):

        # get player's move
        paddle_new_pos = player.next_move(state)

        # validate received move
        paddle_pos = 'paddle' + ('1' if player_name == 'PLAYER 1' else '2') + '_pos'
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

        # check if game time consumed
        curr_time = time.time()
        if curr_time - self.game_begin_time > self.game_max_time:
            # check is game is tied
            # if yes, give extra 30% time
            # if not, declare a winner
            if self.goals['left'] != self.goals['right']:
                winner = max(self.goals, key=(lambda key: self.goals[key]))
                return {'status': 'SUCCESS', 'info': 'Winner by time', 'goals': self.goals,
                        'winner': self.goal_sides[winner].my_display_name}
            elif curr_time - self.game_begin_time > self.game_max_time * 1.3:
                return {'status': 'SUCCESS', 'info': 'Game tied by time', 'goals': self.goals,
                        'winner': None}

        return None
