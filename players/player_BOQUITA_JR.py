import copy
import utils
class Player:
    def __init__(self, paddle_pos, goal_side):
        self.my_display_name = "BOQUITA JR"
        self.future_size = .8
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos
    def next_move(self, current_state):
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' else current_state['paddle2_pos']
        path = estimate_path(current_state, self.future_size)
        self.my_goal_center = {'x': 995/4 if self.my_goal == 'left' else current_state['board_shape'][1],'y': current_state['board_shape'][0]/2}
        #995 * (3/4)
        #current_state['board_shape'][1]
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else 995, 'y': current_state['board_shape'][0]/2}
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
        pt_in_roi = None
        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p

        if pt_in_roi:
            target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1], self.opponent_goal_center, current_state['puck_radius'],current_state['paddle_radius'])
            if self.my_goal is 'left':
                if self.my_paddle_pos['x'] < 995/3.8:
                    direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],'y': target_pos['y'] - self.my_paddle_pos['y']}
                    direction_vector = {k: v / utils.vector_l2norm(direction_vector) for k, v in direction_vector.items()}
                    movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'], utils.distance_between_points(target_pos, self.my_paddle_pos))
                    direction_vector = {k: v * movement_dist for k, v in direction_vector.items()}
                    new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],'y': self.my_paddle_pos['y'] + direction_vector['y']}
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                        self.my_paddle_pos = new_paddle_pos
                else:
                    direction_vector = {'x': self.my_goal_center['x']- self.my_paddle_pos['x'],'y': self.my_goal_center['y']- self.my_paddle_pos['y']}
                    direction_vector = {k: v / utils.vector_l2norm(direction_vector) for k, v in direction_vector.items()}
                    movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'], utils.distance_between_points(self.my_goal_center, self.my_paddle_pos))
                    direction_vector = {k: v * movement_dist for k, v in direction_vector.items()}
                    new_paddle_pos = {'x': self.my_paddle_pos['x']+direction_vector['x'], 'y': self.my_paddle_pos['y'] + direction_vector['y']}
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                        self.my_paddle_pos = new_paddle_pos
            elif self.my_goal is 'right':
                if self.my_paddle_pos['x'] < 995/.5:
                    direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],'y': target_pos['y'] - self.my_paddle_pos['y']}
                    direction_vector = {k: v / utils.vector_l2norm(direction_vector) for k, v in direction_vector.items()}
                    movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'], utils.distance_between_points(target_pos, self.my_paddle_pos))
                    direction_vector = {k: v * movement_dist for k, v in direction_vector.items()}
                    new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],'y': self.my_paddle_pos['y'] + direction_vector['y']}
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                        self.my_paddle_pos = new_paddle_pos
                else:
                    direction_vector = {'x': self.my_goal_center['x']- self.my_paddle_pos['x'],'y': self.my_goal_center['y']- self.my_paddle_pos['y']}
                    direction_vector = {k: v / utils.vector_l2norm(direction_vector) for k, v in direction_vector.items()}
                    movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'], utils.distance_between_points(self.my_goal_center, self.my_paddle_pos))
                    direction_vector = {k: v * movement_dist for k, v in direction_vector.items()}
                    new_paddle_pos = {'x': self.my_paddle_pos['x']+direction_vector['x'], 'y': self.my_paddle_pos['y'] + direction_vector['y']}
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                        self.my_paddle_pos = new_paddle_pos
        return self.my_paddle_pos
def estimate_path(current_state, after_time):
    state = copy.copy(current_state)
    path = []
    while after_time > 0:
        state['puck_pos'] = utils.next_pos_from_state(state)
        if utils.is_goal(state) is not None:
            break
        if utils.next_after_boundaries(state):
            state['puck_speed'] = utils.next_after_boundaries(state)
        path.append((state['puck_pos'], state['puck_speed']))
        after_time -= state['delta_t']
    return path
