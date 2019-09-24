#!/usr/bin/env python3

import sys
import argparse
import importlib

import cv2 as cv
import gamecore


def main(args):
    # load our air hockey board
    board = cv.imread('assests/board_.png')

    # initiallize game state
    state = {}
    state['delta_t'] = 1/100
    state['board_shape'] = board.shape
    state['goal_size'] = 0.45
    state['puck_pos'] = {'x': board.shape[1]/2, 'y': board.shape[0]/2}
    state['puck_speed'] = {'x': 2500, 'y': 2500}
    state['puck_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25)) # Use standard measures
    state['paddle_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25)) # Use standard measures
    state['paddle1_pos'] = {'x': board.shape[1]/20, 'y': board.shape[0]/2}
    state['paddle2_pos'] = {'x': board.shape[1]*9/10, 'y': board.shape[0]/2.5}
    state['paddle1_speed'] = {'x': 0, 'y': 0}
    state['paddle2_speed'] = {'x': 0, 'y': 0}
    state['paddle_max_speed'] = 1000
    epsilon = 10

    # dinamically import Player classes for both players
    # TODO check Player paths exists
    player1_module = importlib.import_module(args.player1)
    player2_module = importlib.import_module(args.player2)

    player1 = player1_module.Player(state['paddle1_pos'], 'left')
    player2 = player2_module.Player(state['paddle2_pos'], 'right')

    # create game with given players
    game_core = gamecore.GameCore(player1, player2, board, state, epsilon)

    # run game
    result = game_core.begin_game()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])

    # Optional arguments
    parser.add_argument("-p1", "--player1", default='player_A', help="Enter Player1 file url without .py extension")
    parser.add_argument("-p2", "--player2", default='player_B', help="Enter Player2 file url without .py extension")

    args = parser.parse_args()
    main(args)

    # try:
    #     sys.exit(main(args))
    # except Exception as exc:
    #     logging.error('Error in main: %s', exc, exc_info=args.verbose)
    #     sys.exit(-1)