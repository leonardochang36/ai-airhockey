import copy
import utils
from decimal import Decimal, ROUND_HALF_UP
import numpy as np

def flatten_state(original_state):
    state = []
    state.append(original_state["puck_pos"]["x"])
    state.append(original_state["puck_pos"]["y"])
    state.append(original_state["puck_speed"]["x"])
    state.append(original_state["puck_speed"]["y"])
    state.append(original_state["paddle1_pos"]["x"])
    state.append(original_state["paddle1_pos"]["y"])
    state.append(original_state["paddle1_speed"]["x"])
    state.append(original_state["paddle1_speed"]["y"])
    return state

def discretize(obs):
    ratios = [
        (ob + abs(lower_bounds[i])) / (upper_bounds[i] - lower_bounds[i])
        for i, ob in enumerate(obs)
    ]
    new_obs = [int(Decimal((buckets[i] - 1) * ratios[i]).to_integral_value(rounding=ROUND_HALF_UP)) for i in range(len(obs))]
    new_obs = [min(buckets[i] - 1, max(0, new_obs[i])) for i in range(len(obs))]
    return tuple(new_obs)

action_dict = {
    0: (0, 0),  # stay
    1: (0, 1),  # up
    2: (0, -1),  # down
    3: (1, 0),  # right
    4: (-1, 0),  # left
    5: (1, 1),  # up-right
    6: (1, -1),  # down-right
    7: (-1, -1),  # down-left
    8: (-1, 1),  # up-left
}
# actions = stay, up,down,right,left, up-right, down-right, down-left, up-left
actions = (9,)
# positionpuckx, positionpucky, speedpuckx,speedpucky,positionplayerx,positionplayery, speedplayerx, speedplayery
buckets = (8, 8, 4, 4, 8, 8, 4, 4)
upper_bounds = [497, 512, 500, 500, 497, 512, 150, 150]
lower_bounds = [0, 0, -500, -500, 0, 0, -150, -150]
step_size = 0.05

q_table = np.load('q_table.npy')

class Player:
    def __init__(self, paddle_pos, goal_side):
        # set your team's name, max. 15 chars
        self.my_display_name = "myTeam"
        self.my_goal = goal_side

    def next_move(self, current_state):
        discretized = discretize(flatten_state(current_state))
        action = np.argmax(q_table[discretized])
        qtx, qty = action_dict[action]
        return {
            "x": qtx * step_size + (current_state['paddle1_pos']['x'] if self.my_goal == 'left' else current_state['paddle2_pos']['x']),
            "y": qty * step_size + (current_state['paddle1_pos']['y'] if self.my_goal == 'left' else current_state['paddle2_pos']['y']),
        }
