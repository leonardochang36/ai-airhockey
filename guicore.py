import copy
import cv2 as cv
import utils

class GUICore:
    def __init__(self, board, show_window=True, save_video=False, video_file=None):
        self.board = board
        # if not board:
        #     raise Exception('ERROR loading board')
        self.show_window = show_window
        self.save_video = save_video
        if show_window:
            cv.namedWindow('AIR HOCKEY')
        if save_video:
            self.out_vid = cv.VideoWriter(video_file, cv.VideoWriter_fourcc('D', 'I', 'V', 'X'), 10,
                                          (self.board.shape[1], self.board.shape[0]))


    def show_current_state(self, frame):        
        cv.imshow('AIR HOCKEY', frame)
        key = cv.waitKey()
        if key == 27: # Esc key to stop
            return -1
        return 0


    def write_current_state(self, frame):
        self.out_vid.write(frame)


    def resolve_gui(self, state):
        # visual feedback
        board_feedback = copy.copy(self.board)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['puck_pos']),
                  state['puck_radius'], (0, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle1_pos']),
                  state['paddle_radius'], (255, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle2_pos']),
                  state['paddle_radius'], (0, 0, 255), -1)

        if self.show_window:
            if self.show_current_state(board_feedback) < 0:
                return -1
        if self.save_video:
            self.write_current_state(board_feedback)
        return 0


    def release_all(self):
        if self.show_window:
            cv.destroyAllWindows()
        if self.save_video:
            self.out_vid.release()
        return
