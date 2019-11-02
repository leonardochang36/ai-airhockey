#!/usr/bin/env python3
""" entry point module

This module implements intefaces for using the ai-airhockey platform.

Modify it under your own responsability, for the competition purposes only
the original version will be used.
"""

import sys
import argparse
import importlib
import random
import logging
import json

import cv2 as cv
import gamecore
import guicore


def main(args):
    # load our air hockey board
    board = cv.imread('assests/board.png')

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
    state['puck_speed'] = {'x': 0, 'y': 700}
    state['paddle1_pos'] = {'x': board.shape[0]*state['goal_size']/2+1, 'y': board.shape[0]/2}
    state['paddle2_pos'] = {'x': board.shape[1] - board.shape[0]*state['goal_size']/2-1,
                            'y': board.shape[0]/2}
    state['paddle1_speed'] = {'x': 0, 'y': 0}
    state['paddle2_speed'] = {'x': 0, 'y': 0}
    state['paddle_max_speed'] = 150
    state['goals'] = {'left': 0, 'right': 0}
    state['is_goal_move'] = None
    epsilon = 1

    # initiallize gui core
    if 'video_file' in args:
        gui_core = guicore.GUICore(board, args.show_window == 'True', True, args.video_file)
    else:
        gui_core = guicore.GUICore(board)

    # dinamically import Player classes for both players
    player1_module = importlib.import_module(args.player1)
    player2_module = importlib.import_module(args.player2)

    # create player instances
    player1 = player1_module.Player(state['paddle1_pos'], 'left')
    player2 = player2_module.Player(state['paddle2_pos'], 'right')

    # create game with given players
    game_core = gamecore.GameCore(player1, player2, board, state, epsilon, gui_core)

    # run game
    result = game_core.begin_game()

    # prepare output
    # convert exception data types to string
    for k, v in result.items():
        if isinstance(v, Exception):
            result[k] = str(type(v).__name__) + ': ' + str(v)

    result['display_names'] = {'left': player1.my_display_name, 'right': player2.my_display_name}

    result = json.dumps(result, skipkeys=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])

    # Optional arguments
    parser.add_argument("-p1", "--player1", default='player_A', help="Enter Player1 file url without .py extension")
    parser.add_argument("-p2", "--player2", default='player_BLAZERS', help="Enter Player2 file url without .py extension")
    parser.add_argument("-vf", "--video_file", default=argparse.SUPPRESS, help="Enter video url to save game, use .avi extension")
    parser.add_argument("-sw", "--show_window", default=True, help="Do you want real-time visual feed?")

    args_ = parser.parse_args()

    try:
        sys.exit(main(args_))
    except Exception as exc:
        logging.error(" Oops... something went wrong :(", exc_info=True)
        status = {'status': 'ERROR', 'info': str(exc), 'goals': None, 'winner': None,
                  'display_names': {'left': 'left', 'right': 'rigth'}}

        print(json.dumps(status, skipkeys=True))
        sys.exit(-1)
