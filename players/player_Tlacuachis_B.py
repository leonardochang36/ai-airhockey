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
import math

class Player: #Constructor
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "Tlacuachis B"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 1
        self.my_goal = goal_side
        self.my_goal_center = {}
        self.opponent_goal_center = {}
        self.my_paddle_pos = paddle_pos

    def next_move(self, current_state):
        """ Function that computes the next move of your paddle

        Implement your algorithm here. This will be the only function
        used by the GameCore. Be aware of abiding all the game rules.

        Returns:
            dict: coordinates of next position of your paddle.
        """


        # update my paddle pos
        # I need to do this because GameCore moves my paddle randomly
        self.my_paddle_pos = current_state['paddle1_pos'] if self.my_goal == 'left' \
                                                              else current_state['paddle2_pos']

        # estimate puck path
        path = estimate_path(current_state, self.future_size)

        # computing both goal centers
        self.my_goal_center = {'x': 0 if self.my_goal == 'left' else current_state['board_shape'][1],
                               'y': current_state['board_shape'][0]/2}
        self.opponent_goal_center = {'x': 0 if self.my_goal == 'right' else current_state['board_shape'][1],
                                     'y': current_state['board_shape'][0]/2}

        # find if puck path is inside my interest area
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 2 -100 ######## 300 campo de vision #########################################################3
        pt_in_roi = None
        for p in path:
            #print(utils.distance_between_points(p[0], self.my_goal_center), '<', roi_radius)
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break
        
    
        #Si el puck esta dentro de la cancha...
        if pt_in_roi:

            #Anti Auto-Gol
            goalR = current_state['board_shape'][0]*0.45/2
            #Checar si el puck esta detras de mi
            puckPos = current_state['puck_pos']
            if self.my_goal is 'left': #Si estoy en la izquierda
                if puckPos['x'] < self.my_paddle_pos['x']: #Si el puck esta detras de mi...
                    #print("Puck esta detras de mi!")
                    #Clalcular direccion del puck
                    path = estimate_path(current_state, self.future_size)
                    target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['board_shape'][0]/2}
                    moveToTarget = True
                    for x in path:
                        if x[1]['x'] > 0: #Puck va hacia la porteria contraria
                            #print("Puck va hacia el enemigo ", x[1]['x'])
                            #Me tengo que mover en diagonal para que no me pegue·············································································
                            #1. Calculo mi vector de direccion hacia mi posicion de defensa de mi paddle
                            target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['board_shape'][0]/2}
                            direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                    'y': target_pos['y'] - self.my_paddle_pos['y']}
                            direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                    for k, v in direction_vector.items()}

                            movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                    utils.distance_between_points(x[0], self.my_paddle_pos))
                            direction_vector = {k: v * movement_dist
                                                    for k, v in direction_vector.items()}
                            
                            #Obtener path del paddle, basandome en la direccion del puck
                            paddlepath = estimate_path_paddle(current_state, self.future_size, self.my_paddle_pos, direction_vector)
                            for y in paddlepath: #Si el path de mi paddle intersecta el path de mi puck
                                if y[0]['x'] > x[0]['x'] - current_state['puck_radius'] and y[0]['x'] < x[0]['x'] + current_state['puck_radius'] and y[0]['y'] > x[0]['y'] - current_state['puck_radius'] and y[0]['y'] < x[0]['y'] + current_state['puck_radius']:
                                    #print("Intersecta!")
                                    if self.my_paddle_pos['y'] > current_state['board_shape'][0]/2:
                                        target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['board_shape'][0] - current_state['puck_radius']}
                                        #print("Me muevo pa arriba")
                                    else:
                                        target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['puck_radius']}
                                        #print("Me muevo pa abajo")

                                else:
                                    target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['board_shape'][0]/2}
                                    #print("Me muevo normal")

                    direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                    'y': target_pos['y'] - self.my_paddle_pos['y']}
                    direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                    for k, v in direction_vector.items()}

                    movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                    utils.distance_between_points(x[0], self.my_paddle_pos))
                    direction_vector = {k: v * movement_dist
                                                    for k, v in direction_vector.items()}                
                    new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'], 'y': self.my_paddle_pos['y'] + direction_vector['y']}
                            
                    if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                            utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                                self.my_paddle_pos = new_paddle_pos


                                       

                else:
                    #Rebote #############################################################################################
                    pos_enemigo = current_state['paddle2_pos']
                    if pos_enemigo['y'] > self.my_goal_center['y']: #Si esta arriba...
                        lineaRebote = current_state['puck_radius']
                        A = current_state['puck_pos']
                        D = {'x': A['x'], 'y': A['y']-lineaRebote}
                        B = self.opponent_goal_center
                    else: #Esta abajo...
                        lineaRebote = current_state['board_shape'][0] - current_state['puck_radius']
                        A = current_state['puck_pos']
                        D = {'x': A['x'], 'y': -(A['y']) + current_state['puck_radius']}
                        B = self.opponent_goal_center

                    #Recta de rebote, donde corta en el eje y del radio del puck
                    m1 = 0 
                    n1 = lineaRebote

                    #Recta entre B y D
                    m2 = (D['y'] - B['y']) / (D['x'] - B['x'])
                    n2 = (B['x']*D['y'] - D['x']*B['y']) / (B['x'] - D['x'])

                    Cx = (n2 - n1) / (m1 - m2)
                    Cy = m1 * Cx + n1
                    C = {'x': Cx, 'y': Cy}
                    #print(current_state['paddle1_pos'])
                    
                    # estimate an aiming position
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                        C, current_state['puck_radius'],
                                        current_state['paddle_radius'])

                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'], #donde quiero ir, donde estoy
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                                            
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                        'y': self.my_paddle_pos['y'] + direction_vector['y']}


                        
                        #Rectas del Triangulo ######################################################################################################
                        if self.my_goal is 'left': #Si estoy en la izquierda
                            R1 = (100,0,(current_state['board_shape'][1]/2)-64,(current_state['board_shape'][0]/2)-64)
                            R2 = (100,(current_state['board_shape'][0]),(current_state['board_shape'][1]/2)-64,(current_state['board_shape'][0]/2)-64)
                        else:   #Si estoy en la derecha
                            R1 = (current_state['board_shape'][1]-100,0, (current_state['board_shape'][1]/2)+64, (current_state['board_shape'][0])/2)
                            R2 = ((current_state['board_shape'][1]/2)+64, (current_state['board_shape'][0])/2, current_state['board_shape'][1]+100, current_state['board_shape'][0])
                        

                        m1 = (R1[1]-R1[3])/(R1[0]-R1[2])
                        m2 = (R2[1]-R2[3])/(R2[0]-R2[2])

                        n1 = (R1[0]*R1[3] - R1[2]*R1[1]) / (R1[0] - R1[2])
                        n2 = (R2[0]*R2[3] - R2[2]*R2[1]) / (R2[0] - R2[2])

                        # Izquierda
                        # R1 | Y =  0.4429065743944637x +  -0.0
                        # R2 | Y = -0.5905420991926182x +  448.0
                        # Derecha
                        # R1 | Y = -0.5905420991926182 x +  587.5893886966551
                        # R2 | Y =  0.5905420991926182 x +  -75.58938869665513
                        
                        #print("Y = ",m1,"x + ", n1)
                        #print("Y = ",m2,"x + ", n2)

                        #Calcular n de ambas rectas paralelas
                        n1p = new_paddle_pos['y'] - new_paddle_pos['x'] * m1
                        n2p = new_paddle_pos['y'] - new_paddle_pos['x'] * m2

                        #Si me movimiento se va a pasar de la recta, no me muevo.
                        if n1p < n1 or n2p > n2:
                            new_paddle_pos = {'x': self.my_paddle_pos['x'], 'y': self.my_paddle_pos['y']}

                        #print("Paralelo contra R1 = Y = ",m1," x + ",n1)
                        #print("Paralelo contra R2 = Y = ",m2," x + ",n2)

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        # Check if computed new position is inside triangle
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                            utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos
                    
            else:   #Si estoy en la derecha ***************************************************************************************************
                if puckPos['x'] > self.my_paddle_pos['x']: #Si el puck esta detras de mi...
                        #print("Puck esta detras de mi!")
                        #Clalcular direccion del puck
                        goalR = current_state['board_shape'][0]*0.45/2
                        
                        path = estimate_path(current_state, self.future_size)
                        target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['board_shape'][0]/2}
                        for x in path:
                            if x[1]['x'] < 0: #Puck va hacia la porteria contraria
                                #print("Puck va hacia el enemigo ", x[1]['x'])
                                #Me tengo que mover en diagonal para que no me pegue·············································································
                                #1. Calculo mi vector de direccion hacia mi posicion de defensa de mi paddle
                                target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['board_shape'][0]/2}
                                direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                        'y': target_pos['y'] - self.my_paddle_pos['y']}
                                direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                        for k, v in direction_vector.items()}

                                movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                        utils.distance_between_points(x[0], self.my_paddle_pos))
                                direction_vector = {k: v * movement_dist
                                                        for k, v in direction_vector.items()}
                                
                                #Obtener path del paddle, basandome en la direccion del puck
                                paddlepath = estimate_path_paddle(current_state, self.future_size, self.my_paddle_pos, direction_vector)
                                for y in paddlepath: #Si el path de mi paddle intersecta el path de mi puck
                                    if y[0]['x'] > x[0]['x'] - current_state['puck_radius'] and y[0]['x'] < x[0]['x'] + current_state['puck_radius'] and y[0]['y'] > x[0]['y'] - current_state['puck_radius'] and y[0]['y'] < x[0]['y'] + current_state['puck_radius']:
                                        #print("Intersecta!")
                                        if self.my_paddle_pos['y'] > current_state['board_shape'][0]/2:
                                            target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['board_shape'][0] - current_state['puck_radius']}
                                            #print("Me muevo pa arriba")
                                        else:
                                            target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['puck_radius']}
                                            #print("Me muevo pa abajo")

                                    else:
                                        target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['board_shape'][0]/2}
                                        #print("Me muevo normal")

                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'],
                                        'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                                        for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                                        utils.distance_between_points(x[0], self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                                        for k, v in direction_vector.items()}                
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'], 'y': self.my_paddle_pos['y'] + direction_vector['y']}
                                
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                                utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                                    self.my_paddle_pos = new_paddle_pos
                                
                else:
                    #Rebote #############################################################################################
                    pos_enemigo = current_state['paddle2_pos']
                    if pos_enemigo['y'] > self.my_goal_center['y']: #Si esta arriba...
                        lineaRebote = current_state['puck_radius']
                        A = current_state['puck_pos']
                        D = {'x': A['x'], 'y': A['y']-lineaRebote}
                        B = self.opponent_goal_center
                    else: #Esta abajo...
                        lineaRebote = current_state['board_shape'][0] - current_state['puck_radius']
                        A = current_state['puck_pos']
                        D = {'x': A['x'], 'y': -(A['y']) + current_state['puck_radius']}
                        B = self.opponent_goal_center

                    #Recta de rebote, donde corta en el eje y del radio del puck
                    m1 = 0 
                    n1 = lineaRebote

                    #Recta entre B y D
                    m2 = (D['y'] - B['y']) / (D['x'] - B['x'])
                    n2 = (B['x']*D['y'] - D['x']*B['y']) / (B['x'] - D['x'])

                    Cx = (n2 - n1) / (m1 - m2)
                    Cy = m1 * Cx + n1
                    C = {'x': Cx, 'y': Cy}
                    #print(current_state['paddle1_pos'])
                    
                    # estimate an aiming position
                    target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                        C, current_state['puck_radius'],
                                        current_state['paddle_radius'])

                    # move to target position, taking into account the max. paddle speed
                    if target_pos != self.my_paddle_pos:
                        direction_vector = {'x': target_pos['x'] - self.my_paddle_pos['x'], #donde quiero ir, donde estoy
                                            'y': target_pos['y'] - self.my_paddle_pos['y']}
                        direction_vector = {k: v / utils.vector_l2norm(direction_vector)
                                            for k, v in direction_vector.items()}

                        movement_dist = min(current_state['paddle_max_speed'] * current_state['delta_t'],
                                            utils.distance_between_points(target_pos, self.my_paddle_pos))
                        direction_vector = {k: v * movement_dist
                                            for k, v in direction_vector.items()}
                                            
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + direction_vector['x'],
                                        'y': self.my_paddle_pos['y'] + direction_vector['y']}


                        
                        #Rectas del Triangulo ######################################################################################################
                        if self.my_goal is 'left': #Si estoy en la izquierda
                            R1 = (100,0,(current_state['board_shape'][1]/2)-64,(current_state['board_shape'][0]/2)-64)
                            R2 = (100,(current_state['board_shape'][0]),(current_state['board_shape'][1]/2)-64,(current_state['board_shape'][0]/2)-64)
                        else:   #Si estoy en la derecha
                            R1 = (current_state['board_shape'][1]-100,0, (current_state['board_shape'][1]/2)+64, (current_state['board_shape'][0])/2)
                            R2 = ((current_state['board_shape'][1]/2)+64, (current_state['board_shape'][0])/2, current_state['board_shape'][1]+100, current_state['board_shape'][0])
                        

                        m1 = (R1[1]-R1[3])/(R1[0]-R1[2])
                        m2 = (R2[1]-R2[3])/(R2[0]-R2[2])

                        n1 = (R1[0]*R1[3] - R1[2]*R1[1]) / (R1[0] - R1[2])
                        n2 = (R2[0]*R2[3] - R2[2]*R2[1]) / (R2[0] - R2[2])

                        # Izquierda
                        # R1 | Y =  0.4429065743944637x +  -0.0
                        # R2 | Y = -0.5905420991926182x +  448.0
                        # Derecha
                        # R1 | Y = -0.5905420991926182 x +  587.5893886966551
                        # R2 | Y =  0.5905420991926182 x +  -75.58938869665513
                        
                        #print("Y = ",m1,"x + ", n1)
                        #print("Y = ",m2,"x + ", n2)

                        #Calcular n de ambas rectas paralelas
                        n1p = new_paddle_pos['y'] - new_paddle_pos['x'] * m1
                        n2p = new_paddle_pos['y'] - new_paddle_pos['x'] * m2

                        #Si me movimiento se va a pasar de la recta, no me muevo.
                        if n1p < n1 or n2p > n2:
                            new_paddle_pos = {'x': self.my_paddle_pos['x'], 'y': self.my_paddle_pos['y']}

                        #print("Paralelo contra R1 = Y = ",m1," x + ",n1)
                        #print("Paralelo contra R2 = Y = ",m2," x + ",n2)

                        # check if computed new position in not inside goal area
                        # check if computed new position in inside board limits
                        # Check if computed new position is inside triangle
                        if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                            utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                            self.my_paddle_pos = new_paddle_pos
                            
        # Jugador se regresa a su porteria si el puck no esta en su lado de la cancha. ################################################3
        else:
            goalR = current_state['board_shape'][0]*0.45/2
            if self.my_goal is 'left': #Si estoy en la izquierda
                target_pos = {'x': current_state['board_shape'][0]*0.45/2, 'y': current_state['board_shape'][0]/2} #current_state['board_shape'][0]/2
            else:   #Si estoy en la derecha
                target_pos = {'x': current_state['board_shape'][1] - goalR, 'y': current_state['board_shape'][0]/2} #current_state['board_shape'][0]/2

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
                    self.my_paddle_pos = new_paddle_pos

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
##############################################################################3
def new_estimate_path(current_state, after_time, puck_pos, puck_speed):
    """ Function that function estimates the next moves in a after_time window

    Returns:
        list: coordinates and speed of puck for next ticks
    """
    state = copy.copy(current_state)
    path = []
    while after_time > 0:
        puck_pos = new_next_pos_from_state(state, puck_pos, puck_speed)
        #if utils.is_goal(state) is not None:
         #   break
        if new_next_after_boundaries(state, puck_pos, puck_speed):##
            puck_speed = new_next_after_boundaries(state, puck_pos, puck_speed) 
        path.append((puck_pos, puck_speed))
        after_time -= state['delta_t']
    return path

def new_next_pos_from_state(state,puck_pos, puck_speed):
    """ Function that computes the next puck position

    From the current state, the next position of the puck is computed
    but not set.

    Returns:
        dict: coordinates
    """
    xn = puck_pos['x'] + puck_speed['x'] * state['delta_t']
    yn = puck_pos['y'] + puck_speed['y'] * state['delta_t']
    return {'x': xn, 'y': yn}

def new_next_after_boundaries(state,puck_pos, puck_speed): ##
    """ Function that computes the next speed after bounce

    If current puck position implies a bounce, the next puck speed
    is computed based on against which border the bounce occurs.
    e.g., horizontal or vertical.

    Returns:
        dict: speed components in x and y
    """
    if new_is_out_of_boundaries(state,puck_pos, puck_speed) == 'horizontal': ##
        return {'x': puck_speed['x'] * -1, 'y': puck_speed['y']}
    if new_is_out_of_boundaries(state,puck_pos, puck_speed) == 'vertical':
        return {'x': puck_speed['x'], 'y': puck_speed['y'] * -1}
    return None


def new_is_out_of_boundaries(state, puck_pos, puck_speed): ##
    """ Function that detects if the puck is out of the board limits.

    Returns:
        None: if is not out of the boundaries
        str: 'horizontal' or 'vertical' if is out of boundaries.
    """
    if new_next_pos_from_state(state,puck_pos,puck_speed)['x'] + state['puck_radius'] >= state['board_shape'][1] \
       or new_next_pos_from_state(state,puck_pos,puck_speed)['x'] - state['puck_radius'] <= 0:
        return 'horizontal'
    if new_next_pos_from_state(state,puck_pos,puck_speed)['y'] + state['puck_radius'] >= state['board_shape'][0] \
       or new_next_pos_from_state(state,puck_pos,puck_speed)['y'] - state['puck_radius'] <= 0:
        return 'vertical'
    return None
############################################################################3
def estimate_path_paddle(current_state, after_time, my_paddle_pos, my_paddle_speed):
    """ Function that function estimates the next moves in a after_time window

    Returns:
        list: coordinates and speed of puck for next ticks
    """

    state = copy.copy(current_state)
    path = []
    while after_time > 0:
        my_paddle_pos = next_paddle_pos_from_state(state,my_paddle_pos,my_paddle_speed)

        if next_paddle_after_boundaries(state,my_paddle_speed,my_paddle_pos):
           my_paddle_speed = next_paddle_after_boundaries(state,my_paddle_speed,my_paddle_pos)
        path.append((my_paddle_pos, my_paddle_speed))
        after_time -= state['delta_t']
    return path


def next_paddle_pos_from_state(current_state, my_paddle_pos, my_paddle_speed):
    """ Function that computes the next puck position

    From the current state, the next position of the puck is computed
    but not set.

    Returns:
        dict: coordinates
    """

    state = copy.copy(current_state)

    xn = my_paddle_pos['x'] + my_paddle_speed['x'] * state['delta_t']
    yn = my_paddle_pos['y'] + my_paddle_speed['y'] * state['delta_t']
    return {'x': xn, 'y': yn}

def next_paddle_after_boundaries(state,my_paddle_speed,my_paddle_pos):
    """ Function that computes the next speed after bounce

    If current puck position implies a bounce, the next puck speed
    is computed based on against which border the bounce occurs.
    e.g., horizontal or vertical.

    Returns:
        dict: speed components in x and y
    """
    if is_out_of_boundaries_paddle(my_paddle_pos,state) == 'horizontal':
        return {'x': my_paddle_speed['x'] * -1, 'y': my_paddle_speed['y']}
    if is_out_of_boundaries_paddle(my_paddle_pos,state) == 'vertical':
        return {'x': my_paddle_speed['x'], 'y': my_paddle_speed['y'] * -1}
    return None

def is_out_of_boundaries_paddle(paddle_pos, state):
    """ Function that detects if a paddle is out of the board limits.

    Returns:
        None: if is not out of the boundaries
        str: 'horizontal' or 'vertical' if is out of boundaries.
    """
    if paddle_pos['x'] + state['paddle_radius'] > state['board_shape'][1] \
       or paddle_pos['x'] - state['paddle_radius'] < 0:
        return 'horizontal'
    if paddle_pos['y'] + state['paddle_radius'] > state['board_shape'][0] \
       or paddle_pos['y'] - state['paddle_radius'] < 0:
        return 'vertical'
    return None

    
