import sys
import socket
import time
import serial
import threading

delay_set = True

static_positions = {
    'home': 'MoveJoints(-2.266,6.800,56.742,0.000,-65.000,-0.000)',
    'ready_for_welder': 'MovePose(-14.113,-174.370,242.565,88.859,-1.310,-90.121)',
    'over_welder': 'MovePose(-12.113,-232.970,229.865,88.859,-1.310,-90.121)',
    'on_welder': 'MovePose(-12.113,-232.970,204.165,88.859,-1.310,-90.121)',
    #second robot info
    'second_robot_home': 'MovePose(210.863,0.000,203.081,-0.000,89.046,0.000)',
    'second_robot_middle_testers': 'MovePose(-0.000,-142.363,203.081,89.046,-0.000,-90.000)',
    'second_robot_ready_for_welder': 'MovePose(-11.235,172.668,221.783,-89.045,-1.360,90.023)',
    'second_robot_over_welder': 'MovePose(-13.935,236.348,188.333,-89.045,-1.360,90.023)',
    'second_robot_on_welder': 'MovePose(-13.935,236.348,158.583,-89.045,-1.360,90.023)',
    'second_robot_over_tester1': 'MovePose(89.000,-146.963,159.581,89.046,0.000,-90.000)',
    'second_robot_on_tester1': 'MovePose(89.000,-146.963,126.581,89.046,-0.000,-90.000)',
    'second_robot_over_tester2': 'MovePose(-120.025,-146.338,155.931,89.046,0.000,-90.000)',
    'second_robot_on_tester2': 'MovePose(-120.025,-146.338,125.056,89.046,0.000,-90.000)',
    'second_robot_good_output': 'MovePose(321.621,13.585,155.933,-64.863,87.753,64.880)',
    'second_robot_bad_output': 'MovePose(-8.575,-311.313,155.931,89.046,0.000,-90.000)'
}

default_speed = 'SetJointVel(' + str(100) + ')'


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

def move_to(robot, position):
    # #check estop
    # check_estop(com)
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
        

def disconnect_robot(robot):
    try:
        robot.send(bytes('DeactivateRobot'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        print(response) 
        #robot.close() 
    except socket.error:
        print('Failed to disconnect')     
            
walle = connect_robot("192.168.0.101", 10000, 'walle')
roger = connect_robot("192.168.0.100", 10000, 'roger')

move_to(walle, static_positions['home'])
move_to(roger, static_positions['second_robot_home'])


time.sleep(3)
disconnect_robot(walle)
disconnect_robot(roger)
sys.exit()
    




