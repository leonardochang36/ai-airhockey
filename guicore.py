""" GUICore module

This module implements all the visual feedback functionalities.
Including, real-time window-based feed and .avi(h264) video file export.
Be sure you have installed OpenCV, ffmpeg, x264.

"""

import copy
import cv2 as cv
import numpy as np

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
            self.out_vid = cv.VideoWriter(video_file, cv.VideoWriter_fourcc(*'H264'), 30,
                                          (self.board.shape[1], int(round(self.board.shape[0] * 1.25))))


    def show_current_state(self, frame, sleep=False):
        cv.imshow('AIR HOCKEY', frame)
        # key = cv.waitKey()
        key = cv.waitKey(1000 if sleep else 5)
        if key == 27: # Esc key to stop
            return -1
        return 0


    def write_current_state(self, frame, sleep=False):
        c = 60 if sleep else 1
        for _ in range(c):
            self.out_vid.write(frame)
        return


    def resolve_gui(self, state, p1, p2):
        board_feedback = np.zeros((int(round(self.board.shape[0] * 1.25)),
                                   self.board.shape[1], self.board.shape[2]), dtype=self.board.dtype)
        # visual feedback
        board_feedback[:self.board.shape[0], :self.board.shape[1]] = copy.copy(self.board)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['puck_pos']),
                  state['puck_radius'], (0, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle1_pos']),
                  state['paddle_radius'], (255, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle2_pos']),
                  state['paddle_radius'], (0, 0, 255), -1)


        if state['is_goal_move'] is None:
            # write text scores
            ## player 1
            ### write team's name
            pos_xy = (20, int(round(self.board.shape[0] * 1.20)))
            text_size = self.draw_text(board_feedback, p1, pos_xy, (255, 0, 0),
                                       (255, 255, 255), 1, 3, 'left')

            ### write score
            pos_xy = (20, int(round(self.board.shape[0] * 1.20 - text_size[1] * 1.5)))
            self.draw_text(board_feedback, str(state['goals']['left']), pos_xy, (255, 0, 0),
                           (255, 255, 255), 2, 3, 'left')

            ## player 2
            ### write team's name
            pos_xy = (self.board.shape[1] - 20, int(round(self.board.shape[0] * 1.20)))
            text_size = self.draw_text(board_feedback, p2, pos_xy, (0, 0, 255),
                                       (255, 255, 255), 1, 3, 'right')

            ### write score
            pos_xy = (self.board.shape[1] - 20, int(round(self.board.shape[0] * 1.20-text_size[1]*1.5)))
            self.draw_text(board_feedback, str(state['goals']['right']), pos_xy, (0, 0, 255),
                           (255, 255, 255), 2, 3, 'right')
        else:
            # write GOAL sign
            pos_xy = (int(board_feedback.shape[1]/2), int(round(self.board.shape[0] * 1.20)))
            self.draw_text(board_feedback, 'GOALLLL for ' + (p1 if state['is_goal_move'] == 'left' else p2),
                           pos_xy, (0, 165, 255), (255, 255, 255), 1.5, 3, 'center')

        if self.save_video:
            self.write_current_state(board_feedback, state['is_goal_move'] is not None)
        if self.show_window:
            if self.show_current_state(board_feedback, state['is_goal_move'] is not None) < 0:
                return -1
        return 0


    def release_all(self):
        if self.show_window:
            cv.destroyAllWindows()
        if self.save_video:
            self.out_vid.release()
        return


    def draw_text(self, img, text, pos_xy, text_color, bg_color, fontscale, thickness,
                  alignment='left'):
        fontface = cv.FONT_HERSHEY_SIMPLEX
        # compute text size in image
        textsize = cv.getTextSize(text, fontface, fontscale, thickness)

        # set text origin according to alignment
        if alignment == 'left':
            textorg = (pos_xy[0], pos_xy[1])
        elif alignment == 'right':
            textorg = (pos_xy[0] - textsize[0][0], pos_xy[1])
        else:
            textorg = (int(round(pos_xy[0] - textsize[0][0]/2)), pos_xy[1])


        # then put the text itself with offset border
        cv.putText(img, text, textorg, fontface, fontscale, bg_color, int(round(thickness * 3)), cv.LINE_AA)
        cv.putText(img, text, textorg, fontface, fontscale, text_color, thickness, cv.LINE_AA)
        return textsize[0]
