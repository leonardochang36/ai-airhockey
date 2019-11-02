import copy
import math
import utils

class Player:
    def __init__(self, paddle_pos, goal_side):
        self.my_display_name = "maxFifteenChars"
        self.future_size = 50
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.my_goal_vertical_tangent_x = 0
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos

        #The speed limit at which the paddle is agressive, even if the puck is approaching
        self.back_off_speed = 1

    def next_move(self, current_state):
        #Update paddle pos
        #Get positions
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle2_pos']
        self.enemy_paddle_pos = current_state['paddle2_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle1_pos']
        
        self.back_off_speed = 3

        if self.my_goal == 'left':
            self.enemy_paddle_speed = current_state['paddle2_speed']
        else:
            self.enemy_paddle_speed = current_state['paddle1_speed']

        #To adjust if the player's goal is on the right
        goal_dir = 1
        if self.my_goal == 'right':
            goal_dir = -1 

        #Get goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        #Get the tangent of the most forward goal position for defence reasons
        if self.my_goal == 'left':
            self.my_goal_vertical_tangent_x = current_state['board_shape'][0] * current_state['goal_size'] / 2
        else:
            self.my_goal_vertical_tangent_x = current_state['board_shape'][1] - (current_state['board_shape'][0] * current_state['goal_size'] / 2)

        #Case 1: The paddle is behind the player but moving towards the enemy goal - try to avoid bouncing it back
        if current_state['puck_speed']['x'] * goal_dir > 0 and current_state['puck_pos']['x'] * goal_dir < self.my_paddle_pos['x'] * goal_dir:
            #Move to the centre of the goal
            new_paddle_pos = move_to_center(current_state, self)
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                self.my_paddle_pos = new_paddle_pos
  
        #Case 2: the puck is moving towards the player's side
        elif current_state['puck_speed']['x'] * goal_dir <= self.back_off_speed:
            #If it's going towards the goal as a direct strike
            whg = will_hit_goal(current_state, self)
            if whg == True:
                #Move to intercept
                #print("Moving to intercept")
                new_paddle_pos = move_to_puck_path(current_state, self)
                if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos
            elif whg == 'R':
                #print("Ricochet period")
                #If it's a ricochet, maintain x with the puck but stay near the goal
                new_paddle_pos = move_to_goal(current_state, self)
                if(new_paddle_pos == -1):
                    new_paddle_pos = self.my_paddle_pos
                if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos
            else:
                #Avoid it, move to centre
                new_paddle_pos = move_to_center(current_state, self)
                if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos

        
        #Case 3: The puck is moving away from the player's goal, get to a defensive position
        elif current_state['puck_speed']['x'] * goal_dir > 0:
            #new_paddle_pos = approximate_future_height(current_state, self)
            """new_paddle_pos = move_to_goal(current_state, self)
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                self.my_paddle_pos = new_paddle_pos"""
            new_paddle_pos = move_to_goal(current_state, self)
            if(new_paddle_pos == -1):
                new_paddle_pos = self.my_paddle_pos
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
            utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                self.my_paddle_pos = new_paddle_pos

        return self.my_paddle_pos

#Move to the centre of the goal
def move_to_center(current_state, self):
    #return_vector = estimate_path_after_enemy_hit(current_state, self)
    vector_to_goal = {'x': self.my_goal_vertical_tangent_x - self.my_paddle_pos['x'], 'y': self.my_goal_center['y'] - self.my_paddle_pos['y']}
    #Get the distance vector
    hyp = math.sqrt(vector_to_goal['x'] ** 2 + vector_to_goal['y'] ** 2)
    #Get the movement vector if max. speed

    max_speed = current_state['paddle_max_speed'] * current_state['delta_t']
    new_paddle_pos = {'x': max_speed * vector_to_goal['x'] / hyp + self.my_paddle_pos['x'], 'y': max_speed * vector_to_goal['y'] / hyp + self.my_paddle_pos['y']}
    #If the move is illegal, stay put
    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
    utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
        return new_paddle_pos
        
    return self.my_paddle_pos

#Check if the puck will go in to the goal on its current trajectory with no ricochets
def will_hit_goal(current_state, self):
    puck_future_pos = copy.copy(current_state['puck_pos'])
    puck_speed = {'x': current_state['puck_speed']['x'] * current_state['delta_t'], 'y': current_state['puck_speed']['y'] * current_state['delta_t']}
    board_limit_x = copy.copy(current_state['board_shape'][1])
    board_limit_y = copy.copy(current_state['board_shape'][0])
    n = 0
    while(1):
        n += 1
        puck_future_pos['x'] += puck_speed['x']
        puck_future_pos['y'] += puck_speed['y']
        #It will intersect the goal
        if is_in_goal_area(puck_future_pos, current_state, self):
            #Will hit
            #print("Will hit ", n)
            return True
        #If the puck goes past the y limit first, assume it's going for the goal with a ricochet
        if puck_future_pos['y'] < 0 or puck_future_pos['y'] > board_limit_y:
            #Might hit
            #print("Might hit ", n)
            #return 'R'
            return True
        #If the puck goes past the x limit before the y and is not in the goal area
        #It's completely possible it bounces off the back board and goes in to the goal
        #But unlikely...

        if puck_future_pos['x'] < 0 or puck_future_pos['x'] > board_limit_x:
            #Won't hit
            return False

#See if a point is in the goal
def is_in_goal_area(position, current_state, self):
    #If the point is less than the radius away from the goal centre, it's in the goal
    #It check the top and bottom points of the puck for a collision
    if utils.distance_between_points(self.my_goal_center, {'x': position['x'], 'y': position['y'] + current_state['puck_radius']}) < current_state['board_shape'][0] * current_state['goal_size'] / 2 \
    or utils.distance_between_points(self.my_goal_center, {'x': position['x'], 'y': position['y'] - current_state['puck_radius']}) < current_state['board_shape'][0] * current_state['goal_size'] / 2:
        return True
    else:
        return False

#Go to the goal to prepare to defend
def move_to_goal(current_state, self):
    #return_vector = estimate_path_after_enemy_hit(current_state, self)
    vector_to_goal = {'x': self.my_goal_vertical_tangent_x - self.my_paddle_pos['x'], 'y': current_state['puck_pos']['y'] - self.my_paddle_pos['y']}
    #Get the distance vector
    hyp = math.sqrt(vector_to_goal['x'] ** 2 + vector_to_goal['y'] ** 2)
    #Get the movement vector if max. speed
    max_speed = current_state['paddle_max_speed'] * current_state['delta_t']

    new_paddle_pos = {'x': max_speed * vector_to_goal['x'] / hyp + self.my_paddle_pos['x'], 'y': max_speed * vector_to_goal['y'] / hyp + self.my_paddle_pos['y']}
    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state):
        return self.my_paddle_pos
    return new_paddle_pos

#Intercept the puck, attempt to aim at the ricochet point
def move_to_puck_path(current_state, self):
    # estimate puck path
    path = estimate_path(current_state, self.future_size)

    # find if puck path is inside my interest area
    roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2
    pt_in_roi = None
    for p in path:
        if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
            pt_in_roi = p
            break

    if pt_in_roi:
        ricochet_point = get_ricochet_point(pt_in_roi[0], self.opponent_goal_center, current_state, self)
        # estimate an aiming position
        target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                            ricochet_point, current_state['puck_radius'],
                            current_state['paddle_radius'])
        
        # move to target position, taking into account the max. paddle speed
        if target_pos != self.my_paddle_pos:
            direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                'y': target_pos['y'] - self.my_paddle_pos['y']}
            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                for k, v in direction_vector.items()}

            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                utils.distance_between_points(target_pos, self.my_paddle_pos))
            direction_vector = {k: v * movement_dist
                                for k, v in direction_vector.items()}
            new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                            'y': self.my_paddle_pos['y'] + direction_vector['y']}

            # check if computed new position in not inside goal area
            # check if computed new position in inside board limits
            if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                
                #print ("Moving to ", target_pos, " with a distance of ", utils.distance_between_points(target_pos, self.my_paddle_pos))
                #print ("Puck distance from target: ", utils.distance_between_points(target_pos, current_state['puck_pos']))
                #Check if the position can be reached
                if utils.distance_between_points(target_pos, self.my_paddle_pos) / 5 < utils.distance_between_points(target_pos, current_state['puck_pos']) / 16:
                    #print ("Can reach ricochet position")
                    self.my_paddle_pos = new_paddle_pos
                else:
                    #print ("Can't reach position by ", utils.distance_between_points(target_pos, self.my_paddle_pos))
                    self.my_paddle_pos = {'x': new_paddle_pos['x'] , 'y': new_paddle_pos['y']}


    return self.my_paddle_pos

#Get the puck has to hit in order to ricochet in to the opponent's goal
def get_ricochet_point(start_point, end_point, current_state, self):
    #Check if enemy is high or low and aim for the opposite
    ricochet_point = {}
    #It the enemy is low
    if self.enemy_paddle_pos['y'] >= current_state['board_shape'][0] / 2:
        #Aim high
        #The equation for x is ((xf - xi) / (yi + yf)) * yi + xi
        ricochet_point['x'] = ((end_point['x'] - start_point['x'])/(start_point['y'] + end_point['y'])) * start_point['y'] + start_point['x']
        ricochet_point['y'] = current_state['puck_radius'] / 2
    else:
        #Aim low
        #The equation for x is ((xf - xi) / ((yM - yi) + (yM - yf)))(yM - yi) + xi
        #Where M is the maximum y value
        M = current_state['board_shape'][0]
        ricochet_point['x'] = ((end_point['x'] - start_point['x']) / ((M - start_point['y']) + (M - start_point['x']))) * (M - start_point['y']) + start_point['x']
        ricochet_point['y'] =  M - (current_state['puck_radius'] / 2)
    return ricochet_point

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
