""" Player module

This is a template/example class for your player.
This is the only file you should modify.

The logic of your hockey robot will be implemented in this class.
Please implement the interface next_move().

The only restrictions here are:
 - to implement a class constructor with the args: paddle_pos, goal_side
 - set self.my_display_name with your team's name, max. 15 characters
 - to implement the function next_move(self, current_state),
    returning the next position of your paddle
"""

import copy
import utils

class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = f'FORANEOS_{goal_side}'

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 30
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos
        self.starting_pos = paddle_pos
        self.last_v_x_direction = None # -1 means left, 1 mins right, 0 means no horizontal speed
        self.puck_path = None
        self.goal_y_coordinates = None
        self.hit_puck_twice = 75

    def aim(self, pos, speed, pos_target, puck_radius, paddle_radius):
        """ Function that computes where to put the paddle for a target puck position

        Args:
            pos: puck position
            speed: puck speed
            pos_target: target position of puck

        Returns:
            dict: paddle position to achieve puck target position
        """

        # target direction vector, normalized, opposite direction
        dir_vector = {'x': pos_target['x'] - pos['x'], 'y': pos_target['y'] - pos['y']}
        dir_vector = {k: -1 * v / utils.vector_l2norm(dir_vector) for k, v in dir_vector.items()}

        # normalized puck speed
        speed_n = {k: v / utils.vector_l2norm(speed)  for k, v in speed.items()}


        intersection_vector = {'x': dir_vector['x'] + speed_n['x'], 'y': dir_vector['y'] + speed_n['y']}
        intersection_vector = {k: v / utils.vector_l2norm(intersection_vector)
                               for k, v in intersection_vector.items()}

        # length of collision point from pos
        intersection_vector = {k: v * (puck_radius + paddle_radius)
                               for k, v in intersection_vector.items()}

        #
        return {'x': pos['x'] + intersection_vector['x'], 'y': pos['y'] + intersection_vector['y']}

    def get_new_paddle_pos(self, target_pos, current_state):
        # move to target position, taking into account the max. paddle speed
        new_paddle_pos = None
        if target_pos and target_pos != self.my_paddle_pos:
            direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                'y': target_pos['y'] - self.my_paddle_pos['y']}
            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                for k, v in direction_vector.items()}

            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                utils.distance_between_points(target_pos, self.my_paddle_pos))
            direction_vector = {k: v * movement_dist
                                for k, v in direction_vector.items()}
            if self.my_goal == 'left':
                if current_state['puck_speed']['x'] >= 0:
                    new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                      'y': self.my_paddle_pos['y'] + direction_vector['y']}
                else:
                    new_paddle_pos = {'x': self.my_paddle_pos['x'],# + direction_vector['x'],
                                      'y': self.my_paddle_pos['y'] + direction_vector['y']}
            else:
                if current_state['puck_speed']['x'] <= 0:
                    new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                      'y': self.my_paddle_pos['y'] + direction_vector['y']}
                else:
                    new_paddle_pos = {'x': self.my_paddle_pos['x'],# + direction_vector['x'],
                                      'y': self.my_paddle_pos['y'] + direction_vector['y']}
        return new_paddle_pos

    def next_move(self, current_state):
        """ Function that computes the next move of your paddle

        Implement your algorithm here. This will be the only function
        used by the GameCore. Be aware of abiding all the game rules.

        Returns:
            dict: coordinates of next position of your paddle.
        """

        #calculate y_coordinates of the goal
        m_puck = None
        if not self.goal_y_coordinates:
            h = current_state['board_shape'][0]
            self.goal_y_coordinates = ((h/2)*(1-current_state['goal_size']), (h/2)*(1+current_state['goal_size']))

        # update my paddle pos
        # I need to do this because GameCore moves my paddle randomly
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle2_pos']
        self.enemy_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'right' \
                                                              else current_state['paddle2_pos']


        # estimate puck path
        path = estimate_path(current_state, self.future_size)

        #recalculate puck path
        v_x = current_state['puck_speed']['x']
        if v_x > 0:
            v_x_direction = 1
        elif v_x < 0:
            v_x_direction = -1
        else:
            v_x_direction = 0

        self.puck_path = calculate_path(current_state)

        self.last_v_x_direction = v_x_direction

        goal_dir = None
        #check if puck is coming to my side, check if it has goal direction
        if self.puck_path and len(self.puck_path) > 0:
            if self.my_goal == "left" and v_x_direction < 0:
                #SI EL PUCK TIENE MENOS DE 2 REBOTES QUE INTERCEPTE EL TIRO A GOL
                if len(self.puck_path) < 3:
                    path_to_my_side = self.puck_path[-1]
                    #goal_dir = goal_direction(path_to_my_side, self.goal_y_coordinates)
                #SI EL PUCK TIENE 2 O MAS REBOTES CHECAMOS SI EL ULTIMO REBOTE ESTA CERCA DE LA PORTERIA
                #PARA INTERCEPTAR MEJOR LA PENULTIMA LINEA EN LUGAR DE LA ULTIMA
                else:
                    if self.puck_path[-1][0][0] < current_state['board_shape'][1] * .20: #20% del largo de la cancha
                        #print('Intercepta 2do')
                        path_to_my_side = self.puck_path[-2]
                    else:
                        path_to_my_side = self.puck_path[-1]
                goal_dir = goal_direction(self.puck_path[-1], self.goal_y_coordinates)
                #slope
                try:
                    #m_puck = (self.puck_path[-1][1][1] - self.puck_path[-1][0][1])/(self.puck_path[-1][1][0] - self.puck_path[-1][0][0])
                    m_puck = (path_to_my_side[1][1] - path_to_my_side[0][1])/(path_to_my_side[1][0] - path_to_my_side[0][0])
                except ZeroDivisionError:
                    m_puck = 0
            elif self.my_goal == "right" and v_x_direction > 0:
                if len(self.puck_path) < 3:
                    path_to_my_side = self.puck_path[-1]
                else:
                    if self.puck_path[-1][0][0] > current_state['board_shape'][1] * .80: #80% del largo de la cancha
                        #print('Intercepta 2do')
                        path_to_my_side = self.puck_path[-2]
                    else:
                        path_to_my_side = self.puck_path[-1]
                goal_dir = goal_direction(self.puck_path[-1], self.goal_y_coordinates)
                #slope
                try:
                    m_puck = (path_to_my_side[1][1] - path_to_my_side[0][1])/(path_to_my_side[1][0] - path_to_my_side[0][0])
                except ZeroDivisionError:
                    m_puck = 0


        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}
        self.bounce_up = {'x': current_state['board_shape'][1] * .60 if self.my_goal == 'left' else current_state['board_shape'][1] * .40,
                          'y': 0}
        self.bounce_down = {'x': current_state['board_shape'][1] * .60 if self.my_goal == 'left' else current_state['board_shape'][1] * .40,
                          'y': current_state['board_shape'][0]}

        if self.enemy_paddle_pos['y'] > current_state['board_shape'][0]/2:
            self.next_target = self.bounce_up
        else:
            self.next_target = self.bounce_down
        #self.next_target = self.opponent_goal_center
        target_pos = None
        #if puck has goal direction, find the nearest point to intercept the puck
        if goal_dir:
            if m_puck != 0:
                m_player = -1/m_puck
                b_player = self.my_paddle_pos['y'] - m_player*self.my_paddle_pos['x']
                #[-1] es ultima linea, [1] es el punto final, y el [1] es coordenada en y de ese punto
                b_puck = path_to_my_side[1][1] - m_puck*path_to_my_side[1][0]
                x = -(b_player - b_puck)/(m_player-m_puck)
                y = m_player * x + b_player
            else:
                x = self.my_paddle_pos['x']
                y = self.puck_path[-1][1][1]

            target_pos = {'x': x, 'y': y}
            while True:
                side = 1 if self.my_goal == "left" else -1
                if utils.is_inside_goal_area_paddle(target_pos,current_state):
                    if m_puck != 0:
                        x = x + side
                        y = m_player * x + b_player
                    else:
                        x = x + side
                    target_pos = {'x':x, 'y': y}
                else:
                    break

            #print(target_pos)

        #if it is already blocking the goal, aim. Or if the shot is not on target.
        err = 0.1
        if (target_pos and abs(self.my_paddle_pos['x'] - target_pos['x'])/target_pos['x'] < err and abs(self.my_paddle_pos['y'] - target_pos['y']) < err) or not goal_dir:
            # find if puck path is inside my interest area
            roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
            pt_in_roi = None
            for p in path:
                if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                    pt_in_roi = p
                    break
            if pt_in_roi:
                # estimate an aiming position
                if self.my_goal == 'left':
                    if current_state['puck_speed']['x'] <= 0 or (abs(current_state['puck_speed']['x']) < self.hit_puck_twice and current_state['goals']['right'] > current_state['goals']['left']):
                        target_pos = self.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.next_target,
                                               #self.opponent_goal_center,
                                               current_state['puck_radius'],
                                               current_state['paddle_radius'])
                    else:
                        target_pos = {'x': self.starting_pos['x'], 'y': self.starting_pos['y']}
                else: #SELF.MY_GOAL == 'RIGHT'
                    if current_state['puck_speed']['x'] >= 0 or (abs(current_state['puck_speed']['x']) < self.hit_puck_twice and current_state['goals']['left'] > current_state['goals']['right']):
                        target_pos = self.aim(pt_in_roi[0], pt_in_roi[1],
                                               self.next_target,
                                               #self.opponent_goal_center,
                                               current_state['puck_radius'],
                                               current_state['paddle_radius'])
                    else:
                        target_pos = {'x': self.starting_pos['x'], 'y': self.starting_pos['y']}

        new_paddle_pos = self.get_new_paddle_pos(target_pos, current_state)

        # check if computed new position in not inside goal area
        # check if computed new position in inside board limits
        if new_paddle_pos:
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                 utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                self.my_paddle_pos = new_paddle_pos
        '''
            else:
                print("invadiendo")
                if m_puck and len(self.puck_path) < 4:
                    while True:
                        if self.my_goal == 'left':
                            if m_puck != 0:
                                target_pos['x'] +=5
                                target_pos['y'] = m_player * target_pos['x'] + b_player
                            else: #m_puck = 0
                                target_pos['x'] += 5
                        else: #SELF. MY GOAL ES RIGHT
                            if m_puck != 0:
                                target_pos['x'] -= 5
                                target_pos['y'] = m_player * target_pos['x'] + b_player
                            else: #m_puck = 0
                                target_pos['x'] -= 5
                        new_paddle_pos = self.get_new_paddle_pos(target_pos, current_state)
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                           utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                           self.my_paddle_pos = new_paddle_pos
                           break
                else:
                    pass
        '''

        # time.sleep(2)
        # return {'x': -12, 'y': -6543}
        return self.my_paddle_pos


def estimate_path(current_state, after_time):
    """ Function that function estimates the next moves in a after_time window

    Returns:
        list: coordinates and speed of puck for next ticks
    """

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

#calculates the path of the puck, returns a list of pairs of points.
#one pair of points denotes a line of the path
def calculate_path(state):
    x1 = state['puck_pos']['x']
    y1 = state['puck_pos']['y']
    v_x = state['puck_speed']['x'] * state['delta_t']
    v_y = state['puck_speed']['y'] * state['delta_t']
    x2 = state['puck_pos']['x'] + v_x
    y2 = state['puck_pos']['y'] + v_y
    h = state['board_shape'][0]
    w = state['board_shape'][1]
    puck_radius = state['puck_radius']
    coord_puck_position = (x1, y1)
    if x2 != x1:
        m = (y2 - y1) / (x2 - x1)
    else:
        m = 0
    b = y1 - m * x1
    if v_x == 0:
        if v_y > 0:
            path_puck = [[coord_puck_position, (x1, h)]]
        else:
            path_puck = [[coord_puck_position, (x1, 0)]]
    elif v_y == 0:
        if v_x > 0:
            path_puck = [[coord_puck_position, (w, y1)]]
        else:
            path_puck = [[coord_puck_position, (0, y1)]]
    else:
        flag = True
        path_puck = []
        while flag:
            if v_x > 0 and v_y > 0: #upper right
                distance_to_x = w - x1 - puck_radius
                distance_to_y = h - y1 - puck_radius
                steps_x = abs(distance_to_x // v_x)
                steps_y = abs(distance_to_y // v_y)
                if steps_x < steps_y:
                    x = x1 + steps_x * v_x
                    y = m * x + b
                    flag = False
                else:
                    y = y1 + steps_y * v_y
                    x = (y - b) / m
                    v_y = -v_y
            elif v_x > 0 and v_y < 0: #lower right
                distance_to_x = w - x1 - puck_radius
                distance_to_y = y1 - puck_radius
                steps_x = abs(distance_to_x // v_x)
                steps_y = abs(distance_to_y // v_y) - 1
                if steps_x < steps_y:
                    x = x1 + steps_x * v_x
                    y = m * x + b
                    flag = False
                else:
                    y = y1 + steps_y * v_y
                    x = (y - b) / m
                    v_y = -v_y
            elif v_x < 0 and v_y < 0: #lower left
                distance_to_x = x1 - puck_radius
                distance_to_y = y1 - puck_radius
                steps_x = abs(distance_to_x // v_x)
                steps_y = abs(distance_to_y // v_y) - 1
                if steps_x < steps_y:
                    x = x1 + steps_x * v_x
                    y = m * x + b
                    flag = False
                else:
                    y = y1 + steps_y * v_y
                    x = (y - b) / m
                    v_y = -v_y
            elif v_x < 0 and v_y > 0: #upper left
                distance_to_x = x1 - puck_radius
                distance_to_y = h - y1 - puck_radius
                steps_x = abs(distance_to_x // v_x)
                steps_y = abs(distance_to_y // v_y)
                if steps_x < steps_y:
                    x = x1 + steps_x * v_x
                    y = m * x + b
                    flag = False
                else:
                    y = y1 + steps_y * v_y
                    x = (y - b) / m
                    v_y = -v_y
            path_puck.append([coord_puck_position, (x, y)])
            x1 = x
            y1 = y
            x2 = x1 + v_x
            y2 = y1 + v_y
            coord_puck_position = (x1, y1)
            if x2 != x1:
                m = (y2 - y1) / (x2 - x1)
            else:
                m = 0
            b = y1 - m * x1
    return path_puck

#checks if the path denoted by <line> will end up between <y_coordinates>
def goal_direction(line, y_coordinates):
    if line[1][1] > (y_coordinates[0] - 100) and line[1][1] < (y_coordinates[1] + 100):
        return True
    else:
        return False
