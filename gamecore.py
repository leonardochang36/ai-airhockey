# import Player
import random
import copy
import cv2 as cv

import utils
import guicore

class GameCore:
    def __init__(self, p1, p2, board, init_state, error_rate):
        self.player1 = p1
        self.player2 = p2
        self.board = board
        self.state = init_state
        self.error_rate = error_rate
        self.gui_core = guicore.GUICore(board)


    def begin_game(self):
        while True:
            self.state['puck_pos'] = utils.next_pos_from_state(self.state)
            if utils.is_goal(self.state) is not None:
                print('GOAL!!! in', utils.is_goal(self.state))
            self.state['puck_speed'] = utils.next_speed(self.state)
            self.state['paddle1_pos'] = self.player1.next_move(self.state)
            self.state['paddle1_pos'] = {k: v + random.uniform(-self.error_rate, self.error_rate)
                                         for k, v in self.state['paddle1_pos'].items()}

            self.state['puck_pos'] = utils.next_pos_from_state(self.state)
            if utils.is_goal(self.state) is not None:
                print('GOAL!!! in', utils.is_goal(self.state))
            self.state['puck_speed'] = utils.next_speed(self.state)
            self.state['paddle2_pos'] = self.player2.next_move(self.state)
            self.state['paddle2_pos'] = {k: v + random.uniform(-self.error_rate, self.error_rate)
                                         for k, v in self.state['paddle2_pos'].items()}

            flag = self.gui_core.show_current_state(self.state)
            if flag < 0:
                break

        return 0
