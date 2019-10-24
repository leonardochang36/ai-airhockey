import copy
import cv2 as cv
import utils
import numpy as np

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
        key = cv.waitKey(5)
        if key == 27: # Esc key to stop
            return -1
        return 0


    def write_current_state(self, frame):
        self.out_vid.write(frame)


    def resolve_gui(self, state, p1, p2):
        board_feedback = np.zeros((int(round(self.board.shape[0] * 1.25)), self.board.shape[1], self.board.shape[2]),
                                  dtype=self.board.dtype)
        # visual feedback
        board_feedback[:self.board.shape[0], :self.board.shape[1]] = copy.copy(self.board)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['puck_pos']),
                  state['puck_radius'], (0, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle1_pos']),
                  state['paddle_radius'], (255, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['paddle2_pos']),
                  state['paddle_radius'], (0, 0, 255), -1)

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


    def draw_text(self, img, text, pos_xy, text_color, bg_color, fontscale, thickness, 
                  alignment='left'):
        fontface = cv.FONT_HERSHEY_SIMPLEX
        # compute text size in image
        textsize = cv.getTextSize(text, fontface, fontscale, thickness)

        # set text origin according to alignment
        if alignment == 'left':
            textorg = (pos_xy[0], pos_xy[1])
        else:
            textorg = (pos_xy[0] - textsize[0][0], pos_xy[1])

        # then put the text itself with offset border
        cv.putText(img, text, textorg, fontface, fontscale, bg_color, int(round(thickness * 3)), cv.LINE_AA)
        cv.putText(img, text, textorg, fontface, fontscale, text_color, thickness, cv.LINE_AA)
        return textsize[0]


    # def draw_teams_scores(self, img, team, score, pos_xy, text_color, bg_color, fontscale,
    #                       thickness, alignment='left'):
        
    #     fontface = cv.FONT_HERSHEY_SIMPLEX
    #     # compute text size in image
    #     textsize = cv.getTextSize(text, fontface, fontscale, thickness)

    #     # set text origin according to alignment
    #     if alignment == 'left':
    #         textorg = (pos_xy[0], pos_xy[1])
    #     else:
    #         textorg = (pos_xy[0] - textsize[0][0], pos_xy[1])

    #     # then put the text itself with offset border
    #     cv.putText(img, team, textorg, fontface, fontscale, bg_color, int(round(thickness * 3)), cv.LINE_AA)
    #     cv.putText(img, team, textorg, fontface, fontscale, text_color, thickness, cv.LINE_AA)

    #     textorg = (textorg[0], textorg[1] - int(round(textsize[0][1] * 1.2)))
    #     cv.putText(img, score, textorg, fontface, fontscale, bg_color, int(round(thickness * 3)), cv.LINE_AA)
    #     cv.putText(img, score, textorg, fontface, fontscale, text_color, thickness, cv.LINE_AA)

    #     return 

        