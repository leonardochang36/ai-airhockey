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
import cv2 as cv

class Player:
    def __init__(self, paddle_pos, goal_side):

        # set your team's name, max. 15 chars
        self.my_display_name = "DJ sven"

        # these belong to my solution,
        # you may erase or change them in yours
        self.future_size = 30
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
        
        
        
        if self.my_goal=='left':
            position=0
        else:
            position=1
        
        
        if position==0:
            position_to_move=main_movement(current_state)
            posx=position_to_move['x']
            posy=position_to_move['y']
            movement=unitary_paddle_direction(posx,posy,current_state)
            roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 4
            upper_boundry=(current_state['board_shape'][1]/2)-current_state['paddle_radius']
            lower_boundry=current_state['board_shape'][1]/8.5
            if current_state['paddle1_pos']['x']+movement['x']<upper_boundry and current_state['paddle1_pos']['x']+movement['x']>lower_boundry:
                        new_paddle_pos = {'x': self.my_paddle_pos['x'] + movement['x'],'y': self.my_paddle_pos['y'] + movement['y']}
                        self.my_paddle_pos = new_paddle_pos
                        #print("I CAN MOVE")
                        
                        #print((movement['x']*movement['x'])+(movement['y']*movement['y']))
                        return self.my_paddle_pos
            else:
                            new_paddle_pos = {'x': self.my_paddle_pos['x']-movement['x'], 'y': self.my_paddle_pos['y'] + movement['y']}
                            self.my_paddle_pos = new_paddle_pos
                            #print("..........")
                            return self.my_paddle_pos
                        #WHAT MOVEMENT IS THE ALGORITHM GOING TO CHOOSE??    
        else:
            
            
            
            position_to_move=main_movement_right(current_state)
            posx=position_to_move['x']
            posy=position_to_move['y']
            movement=unitary_paddle_direction_right(posx,posy,current_state)
            roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 4
            upper_boundry=current_state['board_shape'][1]-(current_state['board_shape'][1]/8.5)
            lower_boundry=(current_state['board_shape'][1]/2)+current_state['paddle_radius']
            if current_state['paddle2_pos']['x']+movement['x']<upper_boundry and current_state['paddle2_pos']['x']+movement['x']>lower_boundry:
                new_paddle_pos = {'x': self.my_paddle_pos['x'] + movement['x'],'y': self.my_paddle_pos['y'] + movement['y']}
                self.my_paddle_pos = new_paddle_pos
                #print("I CAN MOVE")
                
                #print((movement['x']*movement['x'])+(movement['y']*movement['y']))
                return self.my_paddle_pos
            else:
                new_paddle_pos = {'x': self.my_paddle_pos['x']-movement['x'], 'y': self.my_paddle_pos['y'] + movement['y']}
                self.my_paddle_pos = new_paddle_pos
                #print("..........")
                return self.my_paddle_pos
        """
        #print("...................")
        # find if puck path is inside my interest area
        roi_radius = current_state['board_shape'][0] * current_state['goal_size'] * 4
        pt_in_roi = None
        for p in path:
            if utils.distance_between_points(p[0], self.my_goal_center) < roi_radius:
                pt_in_roi = p
                break

        if pt_in_roi:
            # estimate an aiming position
            target_pos = utils.aim(pt_in_roi[0], pt_in_roi[1],
                                   self.opponent_goal_center, current_state['puck_radius'],
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
                print("AAAAAAAAAAA")

                # check if computed new position in not inside goal area
                # check if computed new position in inside board limits
                if utils.is_inside_goal_area_paddle(new_paddle_pos, current_state) is False and \
                     utils.is_out_of_boundaries_paddle(new_paddle_pos, current_state) is None:
                    self.my_paddle_pos = new_paddle_pos

        # time.sleep(2)
        # return {'x': -12, 'y': -6543}
        
        """
        
    
    
    
#make the unitary direction of movement
def unitary_paddle_direction(posx,posy,current_state):

     
    delta={}    
    delta['x']=posx-current_state['paddle1_pos']['x']
    delta['y']=posy-current_state['paddle1_pos']['y']
    posx=posx-current_state['paddle1_pos']['x']
    posy=posy-current_state['paddle1_pos']['y']
    unitx=1
    unity=1
    if posx<0:
        unitx=1
    if posy<0:
        unity=1
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    delta['x']=delta['x']/hypothenus
    
    
    
    delta['y']=delta['y']/hypothenus

    
    #print(current_state['paddle_max_speed'])
    delta['x']=delta['x']*current_state['paddle_max_speed']*current_state['delta_t']*unitx
    #print(delta['x'])
    
    delta['y']=delta['y']*current_state['paddle_max_speed']*current_state['delta_t']*unity
    #print(delta['y'])
    #print("AAAA")
    
    return delta
 
    
def unitary_puck_direction(current_state):
     
     
     delta={}
     delta['x']=(current_state['puck_pos']['x']-current_state['paddle1_pos']['x'])
        
     delta['y']=(current_state['puck_pos']['y']-current_state['paddle1_pos']['y'])
     globalmovement=(math.sqrt((delta['x']*delta['x'])+(delta['y']*delta['y'])))
     delta['x']=delta['x']/globalmovement
     delta['y']=delta['y']/globalmovement
     return delta

def predict_path(current_state):
    goingtogoal=0
    t=1
    hit=0
    #print("Current puck position x: ",current_state['puck_pos']['x'])
    #print("Current puck position y: ",current_state['puck_pos']['y'])
    current={}
    #print("AAAAAAAAAAA")
    #print("Next position: ",current_state['puck_pos']['x']+)
    
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    current['speedx']=current_state['puck_speed']['x']
    current['speedy']=current_state['puck_speed']['y']

    time_engage=0
    while(time_engage<3 or hit==1): 
            current['x']=current['x']+(current['speedx']*current_state['delta_t'])
            current['y']=current['y']+(current['speedy']*current_state['delta_t'])
            time_engage+=current_state['delta_t']

            
            if current['x']>current_state['board_shape'][1]-current_state['puck_radius']:
                #if current['y']>140 and current['y']<370:
                    
                #    goingtogoal=1
                diff=current['x']-current_state['board_shape'][1]
                current['x']=current['x']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
            elif(current['x']<current_state['puck_radius']):
                #diff=current['x']-current['speedx']
                #current['x']=current['y']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
                
                
                
            if current['y']>current_state['board_shape'][0]-current_state['puck_radius']:
                #limit=current_state['board_shape'][0]-current_state['puck_radius']
                
                #diff=current['y']-limit
                
                #diff=current_state['board_shape'][0]-current['y']
                #current['y']=limit-diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                
                #print("BOUNCE")
                
                
            elif(current['y']<current_state['puck_radius']):
                #limit=current_state['puck_radius']
                #diff=limit-current['y']
                
                #current['y']=limit+diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                #print("BOUNCE")
            critical_angleA=0
            
            critical_angleA=critical_angle1(current,current_state)+(math.pi/2)
            critical_angleB=critical_angle2(current,current_state)+math.pi
            
            
            
            critical_posA=critical_position(critical_angleA,current,current_state['puck_radius'],current_state)
            critical_posB=critical_position(critical_angleB,current,current_state['puck_radius'],current_state)
            
            #Check which critical position is nearer
            hypothenusA=distance_point(critical_posA, current_state)
            hypothenusB=distance_point(critical_posB, current_state)
            if hypothenusA>hypothenusB:
                hypothenusA=hypothenusB
                critical_posA=critical_posB
                critical_angleA=critical_angleB
                #print("Best: ",critical_posA)
            #else:
            #    print("Best: ",critical_posA)
            pospoc={}
            pospoc['x']=current['x']
            pospoc['y']=current['y']
            
            #current['x']=+critical_posA['x']
            #current['y']=+critical_posA['y']
            
            flag=can_reach(current_state,current,time_engage)
            #if current['speedx']<0.5:
                #print("Nothing to reach at t: ",time_engage)
                
            #    flag==1
            if flag==1:
                hit=1
                #critical_angle1=critical_angle(current_state)
                print("Puck future position x: ",pospoc['x']," y: ",pospoc['y'],"ENGAGE t: ",time_engage)
                print("FOUND CRITICAL ANGLE ",math.degrees(critical_angleA))
                print("FOUND CRITICAL POSITION x: ",critical_posA['x']," y: ", critical_posA['y']," ENGAGE t ",time_engage)
                return current
            
            #timeengaged+=
    #if current_state[['puck_pos']['x']]
    print("BLOCKER")
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    return current



def can_reach(current_state ,current, t):   
    posx=current_state['paddle1_pos']['x']-current['x']
    posy=current_state['paddle1_pos']['y']-current['y']
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    if hypothenus/current_state['paddle_max_speed']<t:
        #print("***********************************************Can_reach t: ",t)
        return 1
    else:
        return 0
    

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
    #print(path)
    return path

def printxy(delta):
    print("X: ",delta['x'])
    print("X: ",delta['x'])
    
def critical_angle1(current,current_state):
    y1=current_state['board_shape'][0]-current['y']-current_state['puck_radius']
    if y1==0.0:
        return (math.pi)/2
    
    alfa=(current_state['board_shape'][0]/2)/y1
    temp=(current_state['board_shape'][1]-current['x'])/(1+alfa)
    temp=math.atan(temp/y1)
    
    #alfa=(current_state['board_shape'][0]/2)/current_state['paddle1_pos']['y']
    #temp=(current_state['board_shape'][1]-current_state['paddle1_pos']['x'])/(1+alfa)
    #temp=math.degrees(math.atan(temp/current_state['paddle1_pos']['y']))
    
    
    #print(temp)
    return temp


def critical_angle2(current,current_state):
    y1=current['y']-current_state['puck_radius']
    if y1==0.0:
        return 90
    alfa=(current_state['board_shape'][0]/2)/y1
    temp=(current_state['board_shape'][1]-current['x'])/(1+alfa)
    temp=math.atan(temp/y1)
    
    #alfa=(current_state['board_shape'][0]/2)/current_state['paddle1_pos']['y']
    #temp=(current_state['board_shape'][1]-current_state['paddle1_pos']['x'])/(1+alfa)
    #temp=math.degrees(math.atan(temp/current_state['paddle1_pos']['y']))
    
    
    #print(temp)
    return temp


def critical_position(angle,current, hypotenuse,current_state):
    #angle=math.radians(angle)
    pos={}
    pos['x']=math.cos(angle)*hypotenuse+current['x']
    pos['y']=math.sin(angle)*hypotenuse+current['y']
    
    
    sizex=pos['x']-current['x']
    sizey=pos['y']-current['y']
    
    #print("Diff x:", sizex)
    #print("Diff y:", sizey)
    sizex=math.sqrt(sizex**2+sizey**2)
    #print("Puck position: ",current_state['puck_pos'])
    #print("Crit position: ",pos)
    #print("Hypothenus: ",sizex)
    
    return pos


def panic_at_disco(current_state):
    panicpos={}
    panicpos['x']=current_state['board_shape'][1]/8
    panicpos['y']=current_state['board_shape'][0]/2
    return panicpos

def distance_point(current, current_state):
    posx=current_state['paddle1_pos']['x']-current['x']
    posy=current_state['paddle1_pos']['y']-current['y']
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    return hypothenus


def direct_shot(current_state):
    position_to_aim={}
    position_to_aim['x']=current_state['board_shape'][1]
    position_to_aim['y']=current_state['board_shape'][0]/2
    hit=0
    current={}
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    current['speedx']=current_state['puck_speed']['x']
    current['speedy']=current_state['puck_speed']['y']
    print("HELLO")
    time_engage=0
    while(time_engage<5 or hit==1): 
            current['x']=current['x']+(current['speedx']*current_state['delta_t'])
            current['y']=current['y']+(current['speedy']*current_state['delta_t'])
            time_engage+=current_state['delta_t']

            
            if current['x']>current_state['board_shape'][1]-current_state['puck_radius']:
                diff=current['x']-current_state['board_shape'][1]
                current['x']=current['x']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
            elif(current['x']<current_state['puck_radius']):
                #diff=current['x']-current['speedx']
                #current['x']=current['y']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
                
                
                
            if current['y']>current_state['board_shape'][0]-current_state['puck_radius']:
                #limit=current_state['board_shape'][0]-current_state['puck_radius']
                
                #diff=current['y']-limit
                
                #diff=current_state['board_shape'][0]-current['y']
                #current['y']=limit-diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                
                #print("BOUNCE")
                
                
            elif(current['y']<current_state['puck_radius']):
                #limit=current_state['puck_radius']
                #diff=limit-current['y']
                
                #current['y']=limit+diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
               
            critical_angle=0
            
            critical_angle=direct_critical_angle(current,position_to_aim)   #+(math.pi/2)
            
            
            critical_pos=critical_position(critical_angle,current,current_state['puck_radius'],current_state)
            
            #Check which critical position is nearer
            #hypothenus=distance_point(critical_posA, current_state)
                #print("Best: ",critical_posA)
            #else:
            #    print("Best: ",critical_posA)
            pospoc={}
            pospoc['x']=current['x']
            pospoc['y']=current['y']
            
            #current['x']=+critical_posA['x']
            #current['y']=+critical_posA['y']
            
            flag=can_reach(current_state,current,time_engage)
            #if current['speedx']<0.5:
                #print("Nothing to reach at t: ",time_engage)
                
            #    flag==1
            if flag==1:
                hit=1
                #critical_angle1=critical_angle(current_state)
                print("Puck future position x: ",pospoc['x']," y: ",pospoc['y'],"ENGAGE t: ",time_engage)
                print("FOUND CRITICAL ANGLE ",critical_angle)
                print("FOUND CRITICAL POSITION x: ",critical_pos['x']," y: ", critical_pos['y']," ENGAGE t ",time_engage)
                return current
            
            #timeengaged+=
    #if current_state[['puck_pos']['x']]
    print("BLOCKER")
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    return current
    
    
    

def direct_critical_angle(position,goal):
    distancex=goal['x']-position['x']
    distancey=goal['y']-position['y']
    angle=math.tan(distancex/distancey)
    return angle


def main_movement(current_state):
    a=1
    #if a==1:
    
    #current_state['puck_speed']['x'] means going left
    if current_state['puck_speed']['x']<0 and current_state['puck_pos']['x']>current_state['paddle1_pos']['x']:
        #print("THE ALGORITHM CHOSE PREDICT PATH")
        #PREDICT THE PATH
        position_to_move=waluigi(current_state)
    elif(current_state['puck_speed']['x']==0 and current_state['puck_pos']['x']==248.75):
        position_to_move={}
        position_to_move['x']=225.9
        position_to_move['y']=156.2
    else:
        #print("THE ALGORITHM CHOSE PANIC AT DISCO")
        position_to_move=panic_at_disco(current_state)
    return position_to_move


def waluigi(current_state):
    
    position_to_aim={}
    
    hit=0
    current={}
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    current['speedx']=current_state['puck_speed']['x']
    current['speedy']=current_state['puck_speed']['y']
    
    paddlealfa={}
    paddlealfa['x']=current_state['paddle1_pos']['x']
    paddlealfa['y']=current_state['paddle1_pos']['y']
    
    
    
    paddlebeta={}
    paddlebeta['x']=current_state['paddle1_pos']['x']
    paddlebeta['y']=current_state['paddle1_pos']['y']

    
    time_engage=0
    while(time_engage<3 or hit==1): 
            current['x']=current['x']+(current['speedx']*current_state['delta_t'])
            current['y']=current['y']+(current['speedy']*current_state['delta_t'])
            time_engage+=current_state['delta_t']

            if current['x']>current_state['board_shape'][1]-current_state['puck_radius']:
                diff=current['x']-current_state['board_shape'][1]
                current['x']=current['x']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
            elif(current['x']<current_state['puck_radius']):
                #diff=current['x']-current['speedx']
                #current['x']=current['y']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
                
                
            
            if current['y']>current_state['board_shape'][0]-current_state['puck_radius']:
                #limit=current_state['board_shape'][0]-current_state['puck_radius']
                
                #diff=current['y']-limit
                #diff=current_state['board_shape'][0]-current['y']
                #current['y']=limit-diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                
                #print("BOUNCE")
                
                
            elif(current['y']<current_state['puck_radius']):
                #limit=current_state['puck_radius']
                #diff=limit-current['y']
                
                #current['y']=limit+diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
               
            #critical_angle=direct_critical_angle(current,position_to_aim)   #+(math.pi/2)
            
            
            #critical_pos=critical_position(critical_angle,current,current_state['puck_radius'],current_state)
            
            #Check which critical position is nearer
            #hypothenus=distance_point(critical_posA, current_state)
                #print("Best: ",critical_posA)
            #else:
            #    print("Best: ",critical_posA)
            pospoc={}
            pospoc['x']=current['x']
            pospoc['y']=current['y']
            
            
            wapoint1=waluigi_point1(current,current_state)
            wapoint2=waluigi_point2(current,current_state)
            #position_to_aim=waluigi_point(current,current_state)
            #current['x']=+critical_posA['x']
            #current['y']=+critical_posA['y']
            
            
            
            #HOW FAR AWAY FORM THE PUCK IS THE DESTINATION
            paddle_diff1=aim_bott(paddlealfa,wapoint1,current_state['puck_radius'])
            paddle_diff2=aim_bott(paddlebeta,wapoint2,current_state['puck_radius'])
            ###############################################
            paddle_pos1={}
            paddle_pos2={}
            
            
            #THE DESTINATION FOR EACH PADDLE FROM PUCK
            paddle_pos1['x']=current['x']+paddle_diff1['x']
            paddle_pos1['y']=current['y']+paddle_diff1['y']
            
            paddle_pos2['x']=current['x']+paddle_diff2['x']
            paddle_pos2['y']=current['y']+paddle_diff2['y']
            ####################################
            #MOVE BOTH PADDLES
            paddle1_move={}
            paddle2_move={}
            #paddlealfa_move=unitary_paddle_prediction(paddle_pos1,paddle_pos1,current_state)
            #paddlebeta_move=unitary_paddle_prediction(paddle_pos2,paddle_pos1,current_state)
            #paddlealfa['x']=paddlealfa['x']+paddlealfa_move['x']
            #paddlealfa['y']=paddlealfa['y']+paddlealfa_move['y']
            #paddlebeta['x']=paddlebeta['x']+paddlebeta_move['x']
            #paddlebeta['y']=paddlebeta['y']+paddlebeta_move['y']
            #####################################

            
            
            #How much time would each take
            #hypothenus1=math.sqrt((posb['x']-posa['x'])**2+((posb['y']-posa['y'])**2))
            
            
            d1=shortest_distance(paddlealfa,paddle_pos1,current_state)
            d2=shortest_distance(paddlebeta,paddle_pos2,current_state)
            
            
            #Which one takes less time
            #print("TIMES d1: ",d1," d2: ", d2)
            if d2<d1:
                #print("Position2 is closer")
                paddle_pos1=paddle_pos2
                d1=d2
                paddlealfa=paddlebeta
            #else:
            #    print("Position1 is closer")
            
            #if current['speedx']<0.5:
                #print("Nothing to reach at t: ",time_engage)
                
            #    flag==1
            flag=can_reach(current_state,paddle_pos1,time_engage)
            if flag>0:
                hit=1
                #critical_angle1=critical_angle(current_state)
                #print("Future paddle position x: ",paddle_pos1['x']," y: ",paddle_pos1['y'],)
                #print("Puck future position x: ",current['x']," y: ",current['y'],"ENGAGE t: ",time_engage)
                #print("FOUND CRITICAL POSITION ",paddle_pos1)
                #print("Paddle Pos ",paddle_pos1)
                #print
                return paddle_pos1

                
            #timeengaged+=
    #if current_state[['puck_pos']['x']]
    #print("BLOCKER")
    #current['x']=current_state['puck_pos']['x']
    #current['y']=current_state['puck_pos']['y']
    
    
    return panic_at_disco(current_state)

def waluigi_point1(position,current_state):
    shoot_point={}
    shoot_point['x']=current_state['board_shape'][1]-current_state['puck_radius']
    shoot_point['y']=current_state['board_shape'][0]/2
    outsidepoint={}
    outsidepoint['x']=position['x']
    outsidepoint['y']=position['y']+((current_state['board_shape'][0]-position['y']-current_state['puck_radius'])*2)
    m=function_m(outsidepoint,shoot_point)
    
    
    
    shoot_point['y']=current_state['board_shape'][0]-current_state['puck_radius']
    shoot_point['x']=(shoot_point['y']-outsidepoint['y'])/m
    
    return shoot_point

def waluigi_point2(position,current_state):
    shoot_point={}
    shoot_point['x']=current_state['board_shape'][1]-current_state['puck_radius']
    shoot_point['y']=current_state['board_shape'][0]/2
    outsidepoint={}
    outsidepoint['x']=position['x']
    outsidepoint['y']=position['y']-(2*(position['y']-current_state['puck_radius']))
    m=function_m(outsidepoint,shoot_point)
    shoot_point['y']=current_state['puck_radius']
    shoot_point['x']=(shoot_point['y']-outsidepoint['y'])/m
    return shoot_point



    
def function_m(pointa,pointb):
    m=(pointa['y']-pointb['y'])/(pointa['x']-pointb['x'])
    return m



#
def aim_bott(posa,posb,radius):
    
    hypothenus=math.sqrt(((posb['x']-posa['x'])*(posb['x']-posa['x']))+((posb['y']-posa['y'])*(posb['y']-posa['y'])))
    preturn={}
    preturn['x']=0
    preturn['x']=radius*((posb['x']-posa['x'])/hypothenus)
    preturn['y']=radius*((posb['y']-posa['y'])/hypothenus)
    
    
    #print("TOOOOOREROOOO")
    posx=preturn['x']*preturn['x']
    posy=preturn['y']*preturn['y']
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    #print("HYPOTHENUS: ",hypothenus)
    
    
    
    return preturn

def shortest_distance(paddle_pos,current,current_state):
    posx=paddle_pos['x']-current['x']
    posy=paddle_pos['y']-current['y']
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    return hypothenus

    #if hypothenus/current_state['paddle_max_speed']<t:
        #print("Can_reach t: ",t)
    #    return t
    #else:
    #    return 0
    
    
    
    
def unitary_paddle_prediction(origin,destination,current_state):
     
    delta={}    
    delta['x']=destination['x']-origin['x']
    delta['y']=destination['y']-origin['y']
    posx=destination['x']-origin['x']
    posy=destination['x']-origin['x']
    unitx=1
    unity=1
    if posx<0:
        unitx=1
    if posy<0:
        unity=1
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    if hypothenus==0:
        print("ZERO EXCEPTION")
        hypothenus=1
    delta['x']=delta['x']/hypothenus
    
    
    
    delta['y']=delta['y']/hypothenus

    
    #print(current_state['paddle_max_speed'])
    delta['x']=delta['x']*current_state['paddle_max_speed']*current_state['delta_t']*unitx
    #print(delta['x'])
    
    delta['y']=delta['y']*current_state['paddle_max_speed']*current_state['delta_t']*unity
    #print(delta['y'])
    #print("AAAA")

    return delta



def main_movement_right(current_state):
    if current_state['puck_speed']['x']>1 and current_state['puck_pos']['x']<current_state['paddle2_pos']['x']:
        #print("THE ALGORITHM CHOSE PREDICT PATH")
        #PREDICT THE PATH
        position_to_move=waluigi_right(current_state)
    elif(current_state['puck_speed']['x']==0 and current_state['puck_pos']['x']==current_state['board_shape'][1]-248.75):
        position_to_move={}
        position_to_move['x']=current_state['board_shape'][1]-225.9
        position_to_move['y']=156.2
    else:
        #print("THE ALGORITHM CHOSE PANIC AT DISCO")
        position_to_move=panic_at_disco_right(current_state)
        
    return position_to_move

def waluigi_right(current_state):
    position_to_aim={}
    
    hit=0
    current={}
    current['x']=current_state['puck_pos']['x']
    current['y']=current_state['puck_pos']['y']
    current['speedx']=current_state['puck_speed']['x']
    current['speedy']=current_state['puck_speed']['y']
    
    paddlealfa={}
    paddlealfa['x']=current_state['paddle2_pos']['x']
    paddlealfa['y']=current_state['paddle2_pos']['y']
    
    
    
    paddlebeta={}
    paddlebeta['x']=current_state['paddle2_pos']['x']
    paddlebeta['y']=current_state['paddle2_pos']['y']

    
    time_engage=0
    while(time_engage<3 or hit==1): 
            current['x']=current['x']+(current['speedx']*current_state['delta_t'])
            current['y']=current['y']+(current['speedy']*current_state['delta_t'])
            time_engage+=current_state['delta_t']

            if current['x']>current_state['board_shape'][1]-current_state['puck_radius']:
                diff=current['x']-current_state['board_shape'][1]
                current['x']=current['x']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
            elif(current['x']<current_state['puck_radius']):
                #diff=current['x']-current['speedx']
                #current['x']=current['y']-diff
                current['speedx']=current['speedx']*(-1)
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                current['x']=current['x']+(current['speedx']*current_state['delta_t'])
                #print("BOUNCE")
                
                
            
            if current['y']>current_state['board_shape'][0]-current_state['puck_radius']:
                #limit=current_state['board_shape'][0]-current_state['puck_radius']
                
                #diff=current['y']-limit
                #diff=current_state['board_shape'][0]-current['y']
                #current['y']=limit-diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                
                #print("BOUNCE")
                
                
            elif(current['y']<current_state['puck_radius']):
                #limit=current_state['puck_radius']
                #diff=limit-current['y']
                
                #current['y']=limit+diff
                current['speedy']=current['speedy']*(-1)
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
                current['y']=current['y']+(current['speedy']*current_state['delta_t'])
               
            #critical_angle=direct_critical_angle(current,position_to_aim)   #+(math.pi/2)
            
            
            #critical_pos=critical_position(critical_angle,current,current_state['puck_radius'],current_state)
            
            #Check which critical position is nearer
            #hypothenus=distance_point(critical_posA, current_state)
                #print("Best: ",critical_posA)
            #else:
            #    print("Best: ",critical_posA)
            pospoc={}
            pospoc['x']=current['x']
            pospoc['y']=current['y']
            
            
            wapoint1=waluigi_point1_right(current,current_state)
            wapoint2=waluigi_point2_right(current,current_state)
            #position_to_aim=waluigi_point(current,current_state)
            #current['x']=+critical_posA['x']
            #current['y']=+critical_posA['y']
            
            
            
            #HOW FAR AWAY FORM THE PUCK IS THE DESTINATION
            paddle_diff1=aim_bott(paddlealfa,wapoint1,current_state['puck_radius'])
            paddle_diff2=aim_bott(paddlebeta,wapoint2,current_state['puck_radius'])
            ###############################################
            paddle_pos1={}
            paddle_pos2={}
            
            
            #THE DESTINATION FOR EACH PADDLE FROM PUCK
            paddle_pos1['x']=current['x']+paddle_diff1['x']
            paddle_pos1['y']=current['y']+paddle_diff1['y']
            
            paddle_pos2['x']=current['x']+paddle_diff2['x']
            paddle_pos2['y']=current['y']+paddle_diff2['y']
            ####################################
            #MOVE BOTH PADDLES
            paddle1_move={}
            paddle2_move={}
            #paddlealfa_move=unitary_paddle_prediction(paddle_pos1,paddle_pos1,current_state)
            #paddlebeta_move=unitary_paddle_prediction(paddle_pos2,paddle_pos1,current_state)
            #paddlealfa['x']=paddlealfa['x']+paddlealfa_move['x']
            #paddlealfa['y']=paddlealfa['y']+paddlealfa_move['y']
            #paddlebeta['x']=paddlebeta['x']+paddlebeta_move['x']
            #paddlebeta['y']=paddlebeta['y']+paddlebeta_move['y']
            #####################################

            
            
            #How much time would each take
            #hypothenus1=math.sqrt((posb['x']-posa['x'])**2+((posb['y']-posa['y'])**2))
            
            
            d1=shortest_distance(paddlealfa,paddle_pos1,current_state)
            d2=shortest_distance(paddlebeta,paddle_pos2,current_state)
            
            
            #Which one takes less time
            #print("TIMES d1: ",d1," d2: ", d2)
            if d2<d1:
                #print("Position2 is closer")
                paddle_pos1=paddle_pos2
                d1=d2
                paddlealfa=paddlebeta
            #else:
            #    print("Position1 is closer")
            
            #if current['speedx']<0.5:
                #print("Nothing to reach at t: ",time_engage)
                
            #    flag==1
            flag=can_reach_right(current_state,paddle_pos1,time_engage)
            if flag>0:
                hit=1
                #critical_angle1=critical_angle(current_state)
                #print("Future paddle position x: ",paddle_pos1['x']," y: ",paddle_pos1['y'],)
                #print("Puck future position x: ",current['x']," y: ",current['y'],"ENGAGE t: ",time_engage)
                #print("FOUND CRITICAL POSITION ",paddle_pos1)
                #print("Paddle Pos ",paddle_pos1)
                #print
                return paddle_pos1

                
            #timeengaged+=
    #if current_state[['puck_pos']['x']]
    #print("BLOCKER")
    #current['x']=current_state['puck_pos']['x']
    #current['y']=current_state['puck_pos']['y']
    
    
    return panic_at_disco_right(current_state)
    
    
    
def can_reach_right(current_state ,current, t):   
    posx=current_state['paddle2_pos']['x']-current['x']
    posy=current_state['paddle2_pos']['y']-current['y']
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    if hypothenus/current_state['paddle_max_speed']<t:
        #print("***********************************************Can_reach t: ",t)
        return 1
    else:
        return 0
    
def panic_at_disco_right(current_state):
    panicpos={}
    panicpos['x']=(current_state['board_shape'][1])*(7/8)
    panicpos['y']=current_state['board_shape'][0]/2
    return panicpos


def unitary_paddle_direction_right(posx,posy,current_state):

     
    delta={}    
    delta['x']=posx-current_state['paddle2_pos']['x']
    delta['y']=posy-current_state['paddle2_pos']['y']
    posx=posx-current_state['paddle2_pos']['x']
    posy=posy-current_state['paddle2_pos']['y']
    unitx=1
    unity=1
    if posx<0:
        unitx=1
    if posy<0:
        unity=1
    posx=posx*posx
    posy=posy*posy
    hypothenus=posx+posy
    hypothenus=math.sqrt(hypothenus)
    delta['x']=delta['x']/hypothenus
    
    
    
    delta['y']=delta['y']/hypothenus

    
    #print(current_state['paddle_max_speed'])
    delta['x']=delta['x']*current_state['paddle_max_speed']*current_state['delta_t']*unitx
    #print(delta['x'])
    
    delta['y']=delta['y']*current_state['paddle_max_speed']*current_state['delta_t']*unity
    #print(delta['y'])
    #print("AAAA")
    
    return delta

def waluigi_point1_right(position,current_state):
    shoot_point={}
    shoot_point['x']=current_state['puck_radius']
    shoot_point['y']=current_state['board_shape'][0]/2
    outsidepoint={}
    outsidepoint['x']=position['x']
    outsidepoint['y']=position['y']+((current_state['board_shape'][0]-position['y']-current_state['puck_radius'])*2)
    m=function_m(outsidepoint,shoot_point)
    
    
    
    shoot_point['y']=current_state['board_shape'][0]-current_state['puck_radius']
    shoot_point['x']=(shoot_point['y']-outsidepoint['y'])/m
    
    return shoot_point

def waluigi_point2_right(position,current_state):
    shoot_point={}
    shoot_point['x']=current_state['puck_radius']
    shoot_point['y']=current_state['board_shape'][0]/2
    outsidepoint={}
    outsidepoint['x']=position['x']
    outsidepoint['y']=position['y']-(2*(position['y']-current_state['puck_radius']))
    m=function_m(outsidepoint,shoot_point)
    shoot_point['y']=current_state['puck_radius']
    shoot_point['x']=(shoot_point['y']-outsidepoint['y'])/m
    return shoot_point