#this one will have proceudurally generated robot positions and will accept offsets
#it should also read and write its position and offset data to a file
#it will also have a log file and generate a beeping sound when its done with a set of 50
#ideally it will be versatile enough to interface with the testers as well as a welder and 
#thus be a versatile and modular drop-in solution for both tasks, then I will go about 
#retrofitting the other device to be the same

import sys
import socket
import time
import serial
import threading


moves = {
    'home': 'MoveJoints(-2.266,6.800,56.742,0.000,-65.000,-0.000)',
    'over-test': 'MoveJoints(76.443,-13.248,49.473,0.000,-16.267,-1.731)',
    'on-test': 'MoveJoints(76.443,-13.248,49.473,0.000,-16.267,-1.731)',
    'output': 'MoveJoints(-1.592,78.828,-69.333,3.495,-11.135,-3.444)'
}

table_positions = [
    #50th position for tester modular robot:
	#[107.758,-267.493,72.726,98.818,-12.561,-88.285]
]

over_table_positions = [
	#dont know if i will need this or not
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

