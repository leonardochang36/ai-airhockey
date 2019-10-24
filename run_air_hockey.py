#!/usr/bin/env python3

import sys
import argparse
import importlib
import random
import logging

import cv2 as cv
import gamecore
import guicore


def main(args):
    # load our air hockey board
    board = cv.imread('assests/board__.png')

    # initiallize game state
    state = {}
    state['delta_t'] = 1/30
    state['board_shape'] = board.shape
    state['goal_size'] = 0.45
    state['puck_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25)) # Use standard measures
    state['paddle_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25)) # Use standard measures
    x_offset = 0.25 if random.uniform(-1, 1) < 0 else 0.75
    state['puck_pos'] = {'x': board.shape[1] * x_offset, 'y': random.uniform(0 + state['puck_radius'],
                         board.shape[0] - state['puck_radius'])}
    state['puck_speed'] = {'x': 0, 'y': 500}
    state['paddle1_pos'] = {'x': board.shape[1]*0.11, 'y': board.shape[0]/2}
    state['paddle2_pos'] = {'x': board.shape[1]*0.89, 'y': board.shape[0]/2}
    state['paddle1_speed'] = {'x': 0, 'y': 0}
    state['paddle2_speed'] = {'x': 0, 'y': 0}
    state['paddle_max_speed'] = 150
    state['goals'] = {'left': 0, 'right': 0}
    epsilon = 5

    # initiallize gui core
    if 'video_file' in args:
        gui_core = guicore.GUICore(board, args.show_window == 'True', True, args.video_file)
    else:
        gui_core = guicore.GUICore(board)


    # dinamically import Player classes for both players
    # TODO check Player paths exists
    player1_module = importlib.import_module(args.player1)
    player2_module = importlib.import_module(args.player2)

    player1 = player1_module.Player(state['paddle1_pos'], 'left')
    player2 = player2_module.Player(state['paddle2_pos'], 'right')

    # create game with given players
    game_core = gamecore.GameCore(player1, player2, board, state, epsilon, gui_core)

    # run game
    result = game_core.begin_game()
    for k, v in result.items():
        if not isinstance(v, str):
            result[k] = str(type(v).__name__) + ': ' + str(v)
    # print(result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])

    # Optional arguments
    parser.add_argument("-p1", "--player1", default='player_A', help="Enter Player1 file url without .py extension")
    parser.add_argument("-p2", "--player2", default='player_B', help="Enter Player2 file url without .py extension")
    parser.add_argument("-vf", "--video_file", default=argparse.SUPPRESS, help="Enter video url to save game, use .avi extension")
    parser.add_argument("-sw", "--show_window", default=True, help="Do you want real-time visual feed?")

    args = parser.parse_args()

    try:
        sys.exit(main(args))
    except Exception as exc:
        logging.error(" Oops... something went wrong :(", exc_info=True)
        status = {'status': 'ERROR', 'info': exc, 'goals': None, 'winner': None}
        print(status)
        sys.exit(-1)