import copy
import cv2 as cv
import utils

class GUICore:
    def __init__(self, board):
        self.board = board
        # if not board:
        #     raise Exception('ERROR loading board')
        cv.namedWindow('AIR HOCKEY')

    def show_current_state(self, state):
        # visual feedback
        board_feedback = copy.copy(self.board)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['puck_pos']), state['puck_radius'], (0, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle1_pos']), state['paddle_radius'], (255, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle2_pos']), state['paddle_radius'], (0, 0, 255), -1)
        cv.imshow('AIR HOCKEY', board_feedback)

        key = cv.waitKey(10)
        if key == 27: # Esc key to stop
            return -1
        return 0
