import sys
import socket
import time
import serial
import threading


moves = {
    'home': 'MoveJoints(-2.266,6.800,56.742,0.000,-65.000,-0.000)',
    'pre-weld': 'MoveJoints(76.443,-13.248,49.473,0.000,-16.267,-1.731)',
    'over_welder': 'MoveJoints(89.199,26.076,18.142,50.074,-56.278,-33.342)',
    'on_welder': 'MoveJoints(89.199,35.405,24.106,43.964,-66.753,-20.624)',
    'on_welder_drop': 'MoveJoints(89.199,29.858,21.485,46.820,-61.010,-27.098)',
    #'ready_to_bop': 'MoveJoints(73.143,13.029,36.475,-4.375,-46.785,1.089)',
    #'bop': 'MoveJoints(74.327,16.840,31.432,-2.810,-45.506,0.118)',
    'output': 'MoveJoints(-1.592,78.828,-69.333,3.495,-11.135,-3.444)'
}

table_positions = [

    #on table positions
    'MovePose(-79.126,-140.314,80.000,93.502,26.170,-92.872)',  #on 0
    'MovePose(-51.407,-140.314,80.000,93.502,26.170,-92.872)',  #on 1
    'MovePose(-23.688,-140.314,80.000,93.502,26.170,-92.872)',  #on 2
    'MovePose(34.971,-139.099,80.000,89.623,-11.555,-91.853)',  #on 3
    'MovePose(62.690,-139.099,80.000,89.623,-11.555,-91.853)',  #on 4
    'MovePose(90.409,-139.099,80.000,89.623,-11.555,-91.853)',  #on 5
    'MovePose(118.128,-139.099,80.000,89.623,-11.555,-91.853)', #on 6
    'MovePose(145.847,-139.099,80.000,89.623,-11.555,-91.853)', #on 7
    'MovePose(173.566,-139.099,80.000,89.623,-11.555,-91.853)', #on 8
    'MovePose(201.285,-139.099,80.000,89.623,-11.555,-91.853)', #on 9


    'MovePose(-79.126,-168.033,80.000,93.502,26.170,-92.872)',  #on 10
    'MovePose(-51.407,-168.033,80.000,93.502,26.170,-92.872)',  #on 11
    'MovePose(-23.688,-168.033,80.000,93.502,26.170,-92.872)',  #on 12
    'MovePose(34.971,-166.818,80.000,89.623,-11.555,-91.853)',  #on 13
    'MovePose(62.690,-166.818,80.000,89.623,-11.555,-91.853)',  #on 14
    'MovePose(90.409,-166.818,80.000,89.623,-11.555,-91.853)',  #on 15
    'MovePose(118.128,-166.818,80.000,89.623,-11.555,-91.853)', #on 16
    'MovePose(145.847,-166.818,80.000,89.623,-11.555,-91.853)', #on 17
    'MovePose(173.566,-166.818,80.000,89.623,-11.555,-91.853)', #on 18
    'MovePose(201.285,-166.818,80.000,89.623,-11.555,-91.853)', #on 19


    'MovePose(-79.126,-195.752,80.000,93.502,26.170,-92.872)',  #on 20
    'MovePose(-51.407,-195.752,80.000,93.502,26.170,-92.872)',  #on 21
    'MovePose(-23.688,-195.752,80.000,93.502,26.170,-92.872)',  #on 22
    'MovePose(34.971,-194.537,80.000,89.623,-11.555,-91.853)',  #on 23
    'MovePose(62.690,-194.537,80.000,89.623,-11.555,-91.853)',  #on 24
    'MovePose(90.409,-194.537,80.000,89.623,-11.555,-91.853)',  #on 25
    'MovePose(118.128,-194.537,80.000,89.623,-11.555,-91.853)', #on 26
    'MovePose(145.847,-194.537,80.000,89.623,-11.555,-91.853)', #on 27
    'MovePose(173.566,-194.537,80.000,89.623,-11.555,-91.853)', #on 28
    'MovePose(200.317,-195.308,80.548,93.876,-11.377,-91.634)', #on 29


    'MovePose(-79.126,-223.471,80.000,93.502,26.170,-92.872)',  #on 30
    'MovePose(-51.407,-223.471,80.000,93.502,26.170,-92.872)',  #on 31
    'MovePose(-23.688,-223.471,80.000,93.502,26.170,-92.872)',  #on 32
    'MovePose(18.561,-219.072,80.000,88.776,7.030,-89.850)',    #on 33
    'MovePose(46.280,-219.072,80.000,88.776,7.030,-89.850)',    #on 34
    'MovePose(73.999,-219.072,80.000,88.776,7.030,-89.850)',    #on 35
    'MovePose(101.718,-219.072,80.000,88.776,7.030,-89.850)',   #on 36
    'MovePose(129.437,-219.072,80.000,88.776,7.030,-89.850)',   #on 37
    'MovePose(157.156,-219.072,80.000,88.776,7.030,-89.850)',   #on 38
    'MovePose(184.875,-219.072,80.000,88.776,7.030,-89.850)',   #on 39


    'MovePose(-79.126,-251.190,80.000,93.502,26.170,-92.872)', #on 40
    'MovePose(-51.407,-251.190,80.000,93.502,26.170,-92.872)', #on 41
    'MovePose(-23.688,-251.190,80.000,93.502,26.170,-92.872)', #on 42
    'MovePose(-0.036,-251.535,80.000,89.960,30.224,-89.299)',  #on 43
    'MovePose(27.683,-251.535,80.000,89.960,30.224,-89.299)',  #on 44
    'MovePose(55.402,-251.535,80.000,89.960,30.224,-89.299)',  #on 45
    'MovePose(83.121,-251.535,80.000,89.960,30.224,-89.299)',  #on 46
    'MovePose(110.840,-251.535,80.000,89.960,30.224,-89.299)', #on 47
    'MovePose(138.559,-251.535,80.000,89.960,30.224,-89.299)', #on 48
    'MovePose(166.278,-251.535,80.000,89.960,30.224,-89.299)' #on 49
]

over_table_positions = [

    #over table positions
    'MovePose(-79.126,-140.314,140.130,93.502,26.170,-92.872)',  #over 0
    'MovePose(-51.407,-140.314,140.130,93.502,26.170,-92.872)',  #over 1
    'MovePose(-23.688,-140.314,140.130,93.502,26.170,-92.872)',  #over 2
    'MovePose(34.971,-139.099,140.130,89.623,-11.555,-91.853)',  #over 3
    'MovePose(62.690,-139.099,140.130,89.623,-11.555,-91.853)',  #over 4
    'MovePose(90.409,-139.099,140.130,89.623,-11.555,-91.853)',  #over 5
    'MovePose(118.128,-139.099,140.130,89.623,-11.555,-91.853)', #over 6
    'MovePose(145.847,-139.099,140.130,89.623,-11.555,-91.853)', #over 7
    'MovePose(173.566,-139.099,140.130,89.623,-11.555,-91.853)', #over 8
    'MovePose(201.285,-139.099,140.130,89.623,-11.555,-91.853)', #over 9


    'MovePose(-79.126,-168.033,140.130,93.502,26.170,-92.872)',  #over 10
    'MovePose(-51.407,-168.033,140.130,93.502,26.170,-92.872)',  #over 11
    'MovePose(-23.688,-168.033,140.130,93.502,26.170,-92.872)',  #over 12
    'MovePose(34.971,-166.818,140.130,89.623,-11.555,-91.853)',  #over 13
    'MovePose(62.690,-166.818,140.130,89.623,-11.555,-91.853)',  #over 14
    'MovePose(90.409,-166.818,140.130,89.623,-11.555,-91.853)',  #over 15
    'MovePose(118.128,-166.818,140.130,89.623,-11.555,-91.853)', #over 16
    'MovePose(145.847,-166.818,140.130,89.623,-11.555,-91.853)', #over 17
    'MovePose(173.566,-166.818,140.130,89.623,-11.555,-91.853)', #over 18
    'MovePose(201.285,-166.818,140.130,89.623,-11.555,-91.853)', #over 19


    'MovePose(-79.126,-195.752,140.130,93.502,26.170,-92.872)',  #over 20
    'MovePose(-51.407,-195.752,140.130,93.502,26.170,-92.872)',  #over 21
    'MovePose(-23.688,-195.752,140.130,93.502,26.170,-92.872)',  #over 22
    'MovePose(34.971,-194.537,140.130,89.623,-11.555,-91.853)',  #over 23
    'MovePose(62.690,-194.537,140.130,89.623,-11.555,-91.853)',  #over 24
    'MovePose(90.409,-194.537,140.130,89.623,-11.555,-91.853)',  #over 25
    'MovePose(118.128,-194.537,140.130,89.623,-11.555,-91.853)', #over 26
    'MovePose(145.847,-194.537,140.130,89.623,-11.555,-91.853)', #over 27
    'MovePose(173.566,-194.537,140.130,89.623,-11.555,-91.853)', #over 28
    'MovePose(201.285,-194.537,140.130,89.623,-11.555,-91.853)', #over 29


    'MovePose(-79.126,-223.471,140.130,93.502,26.170,-92.872)',  #over 30
    'MovePose(-51.407,-223.471,140.130,93.502,26.170,-92.872)',  #over 31
    'MovePose(-23.688,-223.471,140.130,93.502,26.170,-92.872)',  #over 32
    'MovePose(18.561,-219.072,140.130,88.776,7.030,-89.850)',    #over 33
    'MovePose(46.280,-219.072,140.130,88.776,7.030,-89.850)',    #over 34
    'MovePose(73.999,-219.072,140.130,88.776,7.030,-89.850)',    #over 35
    'MovePose(101.718,-219.072,140.130,88.776,7.030,-89.850)',   #over 36
    'MovePose(129.437,-219.072,140.130,88.776,7.030,-89.850)',   #over 37
    'MovePose(157.156,-219.072,140.130,88.776,7.030,-89.850)',   #over 38
    'MovePose(184.875,-219.072,140.130,88.776,7.030,-89.850)',   #over 39


    'MovePose(-79.126,-251.190,140.130,93.502,26.170,-92.872)', #over 40
    'MovePose(-51.407,-251.190,140.130,93.502,26.170,-92.872)', #over 41
    'MovePose(-23.688,-251.190,140.130,93.502,26.170,-92.872)', #over 42
    'MovePose(-0.036,-251.535,140.130,89.960,30.224,-89.299)',  #over 43
    'MovePose(27.683,-251.535,140.130,89.960,30.224,-89.299)',  #over 44
    'MovePose(55.402,-251.535,140.130,89.960,30.224,-89.299)',  #over 45
    'MovePose(83.121,-251.535,140.130,89.960,30.224,-89.299)',  #over 46
    'MovePose(110.840,-251.535,140.130,89.960,30.224,-89.299)', #over 47
    'MovePose(138.559,-251.535,140.130,89.960,30.224,-89.299)', #over 48
    'MovePose(166.278,-251.535,140.130,89.960,30.224,-89.299)' #over 49
]

estop_state = 0; #default to the welder being on

delay_set = False
if input('Do the slow full start? [y/n]: ') == 'y':
    delay_set = True
    
set_default_speed = int(input('Default speed: '))
set_slow_speed = int(input('Slow speed: '))

default_speed = 'SetJointVel(' + str(set_default_speed) + ')'
slower_pickup_speed = 'SetJointVel(' + str(set_slow_speed) + ')'

def connect_robot(ip, port, name_of_robot):
    try:
        robot_socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket for robot at: ' + ip)
        return -1

    print('Socket Created for ' + name_of_robot +  ' at: ' + ip)
    #log_file.write('Socket Created for ' + name_of_robot +  ' at: ' + ip + '\n')

    robot_socket_connection.connect((ip, port))

    print('Socket Connected to robot at: ' + ip)
    #log_file.write('Socket Connected to robot at: ' + ip + '\n')

    response = robot_socket_connection.recv(1024).decode('ascii')
    print(response)

    try:
        robot_socket_connection.send(bytes('ActivateRobot'+'\0','ascii'))
        if delay_set == True:
            time.sleep(15)
        response = robot_socket_connection.recv(1024).decode('ascii')
        print(response) 
    except socket.error:
        print('Failed to Activate robot at: ' + ip)
        return -1

    try:
        robot_socket_connection.send(bytes('Home'+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        print(response)
    except socket.error:
        print('Failed to home robot at: ' + ip)
        return -1

    try:
        robot_socket_connection.send(bytes(default_speed+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to set joint velocity for robot at: ' + ip)
        return -1

    try:
        robot_socket_connection.send(bytes('MoveJoints(0,0,0,0,16.5,0)'+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        robot_socket_connection.send(bytes('gripperopen()'+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to go to neutral position for robot at: ' + ip)
        return -1

    print('\n')
    return robot_socket_connection

def check_estop(com):
    #check for and handle estop 
    global estop_state
    if com.in_waiting:
        line = com.readline()
        info = line.strip().decode('utf-8')
        if info == "estop":
            estop_state = 1; #estop was hit
            estopstart = time.time()
            outfile = open('partslog.txt', 'a')
            outfile.write('E-Stop was hit at: ' + str(estopstart) + '\n')
            outfile.close()
            print('E-Stop was hit')

    if estop_state == 1:
        while True:
            if com.in_waiting:
                line = com.readline()
                info = line.strip().decode('utf-8')
                if info == "resume":
                    estop_state = 0; #estop was hit
                    estopend = time.time()
                    outfile = open('partslog.txt', 'a')
                    outfile.write('E-Stop was reset after: ' + str(estopend - estopstart) + 'seconds\n')
                    outfile.close()
                    print('E-Stop was reset')
                    break
            else:
                time.sleep(0.05)
    #end of check for estop 

def move_to(robot, position):
    #check estop
    check_estop(com)
    try:
        robot.send(bytes(position+'\0','ascii'))
        #response = robot.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to move robot')
    return 0

def open_gripper(robot):
    try:
        robot.send(bytes('gripperopen'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        robot.send(bytes('delay(0.1)'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        #print(response)
        time.sleep(.1)
    except socket.error:
        print('Failed to open gripper')
        
def close_gripper(robot):
    try:
        robot.send(bytes('gripperclose'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        robot.send(bytes('delay(0.1)'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        #print(response)
        time.sleep(.1)
    except socket.error:
        print('Failed to close gripper')

def disconnect_robot(robot):
    try:
        robot.send(bytes('DeactivateRobot'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        print(response) 
        #robot.close() 
    except socket.error:
        print('Failed to disconnect') 

def connect_control(serial_port, baud_rate):
	ser = serial.Serial(serial_port, baud_rate, timeout=1)
	time.sleep(2)
	ser.reset_input_buffer()
	print('connected to control unit\n')
	return ser

def start_welder(com):
    com.write('1'.encode())
    time.sleep(0.1)
    while True:
        if com.in_waiting:
            line = com.readline()
            info = line.strip().decode('utf-8')
            if info == "Home":
                com.reset_input_buffer()
                break
            if info == "estop":
                estop_state = 1; #estop was hit
                #break
        else:
            time.sleep(0.0)

def get_valve_from_table(robot, index):
    move_to(robot, over_table_positions[index])
    open_gripper(robot)
    robot.send(bytes(slower_pickup_speed+'\0','ascii'))
    move_to(robot, table_positions[index])
    close_gripper(robot)
    move_to(robot, over_table_positions[index])
    robot.send(bytes(default_speed+'\0','ascii'))
    move_to(robot, moves['home'])

def put_valve_into_welder(robot):
    move_to(robot, moves['pre-weld'])
    robot.send(bytes(slower_pickup_speed+'\0','ascii'))
    move_to(robot, moves['over_welder'])
    move_to(robot, moves['on_welder_drop'])
    open_gripper(robot)
    robot.send(bytes(default_speed+'\0','ascii'))
    move_to(robot, moves['over_welder'])
    move_to(robot, moves['pre-weld'])
    #move_to(robot, moves['home'])

def get_valve_from_welder(robot):
    #move_to(robot, moves['pre-weld'])
    #move_to(robot, moves['ready_to_bop'])
    #move_to(robot, moves['bop'])
    move_to(robot, moves['pre-weld'])
    move_to(robot, moves['over_welder'])
    robot.send(bytes(slower_pickup_speed+'\0','ascii'))
    move_to(robot, moves['on_welder'])
    close_gripper(robot)
    move_to(robot, moves['over_welder'])
    robot.send(bytes(default_speed+'\0','ascii'))
    move_to(robot, moves['pre-weld'])
    move_to(robot, moves['home'])

def put_valve_into_output_bin(robot):
    move_to(robot, moves['output'])
    open_gripper(robot)
    move_to(robot, moves['home'])


#comport = input('enter the com port for the welder control: ')
comport = '/dev/ttyACM0'
com = connect_control(comport, 9600)
walle = connect_robot("192.168.0.101", 10000, 'walle')

while True:
    user_time_start = time.time()
    print('\nReady for next set')
    num_cycles = 50#int(input('How many valves to make: '))
    next = input('Press enter to continue')
    
    start = time.time()
    for i in range(num_cycles):
        com.reset_input_buffer()
        get_valve_from_table(walle, i)
        put_valve_into_welder(walle)
        time.sleep(.2)
        start_welder(com)
        time.sleep(.2)
        get_valve_from_welder(walle)
        put_valve_into_output_bin(walle)
        
    end = time.time()
    print('the last: ' + str(num_cycles) + ' valves took: ' + str(end - start) + ' seconds for the robot to complete\n')
    print('and ' + str(start - user_time_start) + ' for the board flip and reload\n')
    print('total production time was: ' + str(end - user_time_start) + '\n')
    outfile = open('partslog.txt', 'a')
    outfile.write('50 @ time: ' + str(end) + ' total production time was: ' 
                    + str(end - user_time_start) + ' robot took: ' + str(end - start) 
                    + ' seconds and user took: ' + str(start - user_time_start) + '\n')
    outfile.close()

