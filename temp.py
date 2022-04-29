import sys
import socket
import time
import serial
import threading

x_adj = 0
y_adj = 0
z_adj = 0

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

set_default_speed = int(input('Default speed: '))
set_slow_speed = int(input('Slow speed: '))

default_speed = 'SetJointVel(' + str(set_default_speed) + ')'
slower_pickup_speed = 'SetJointVel(' + str(set_slow_speed) + ')'

def generate_nth_position(i, z_increase):
	#position 50 (i = 49) 
	#on part: [-123.077,291.225,103.731,-92.322,0.916,89.977]
	#over part: [-123.077,291.225,157.156,-92.322,0.916,89.977]

	dist_between_parts = 27.719
	start_pos_x = 125.703 + x_adj
	start_pos_y = 176.158 + y_adj
	start_pos_z = 105.115 + z_adj   #70.729
	orientation_data = '-89.553,-0.079,89.288)'
	header_string = 'MovePose('
	x_offset = (i % 10) * dist_between_parts * -1.0
	y_offset = (i // 10) * dist_between_parts + ((i % 10) * .31)
	z_offset = z_increase

	if i == 49 and z_increase > 50.000:
		orientation_data = '-92.322,0.916,89.977)'
		start_pos_x = -123.077
		start_pos_y = 291.225
		start_pos_z = 103.731
		x_offset = 0
		y_offset = 0
		z_offset = 50.000

	position_n = header_string + str(round(start_pos_x + x_offset, 3)) + ',' + str(round(start_pos_y + y_offset, 3)) + ',' + str(round(start_pos_z + z_offset, 3)) + ',' + orientation_data
	return position_n

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

def put_part_into_welder_start_welder_and_get_next_part(robot, i, comport):
	if i == 0:
		open_gripper(robot)
		move_to(robot, generate_nth_position(i, 100))
		#time.sleep(0.1)
		move_to(robot, generate_nth_position(i, 0))
		close_gripper(robot)
		move_to(robot, generate_nth_position(i, 100))
		move_to(robot, static_positions['home'])

	move_to(robot, static_positions['ready_for_welder'])
	move_to(robot, static_positions['over_welder'])
	move_to(robot, static_positions['on_welder'])
	open_gripper(robot)
	move_to(robot, static_positions['over_welder'])
	move_to(robot, static_positions['ready_for_welder'])

	comport.write('W'.encode())

	move_to(robot, static_positions['home'])

	if i < 49:
		move_to(robot, generate_nth_position(i+1, 100))
		#time.sleep(0.1)
		move_to(robot, generate_nth_position(i+1, 0))
		close_gripper(robot)
		move_to(robot, generate_nth_position(i+1, 100))
		move_to(robot, static_positions['home'])

	while True:
		if comport.in_waiting:
			line = comport.readline()
			info = line.strip().decode('utf-8')
			if info == "Welder Home":
				comport.reset_input_buffer()
				break
		time.sleep(0.05)

def put_part_into_tester_1(robot, comport):
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_over_tester1'])
	move_to(robot, static_positions['second_robot_on_tester1'])
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester1'])
	comport.write('1'.encode())
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_home'])

def put_part_into_tester_2(robot, comport):
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_over_tester2'])
	move_to(robot, static_positions['second_robot_on_tester2'])
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester2'])
	comport.write('2'.encode())
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_home'])

def put_in_correct_output(robot, pass_or_fail_value):
	if pass_or_fail_value == 1:
		move_to(robot, static_positions['second_robot_good_output'])
	else if pass_or_fail_value == 0:
		move_to(robot, static_positions['second_robot_bad_output'])
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_home'])

def get_part_from_tester_1(robot):
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_over_tester1'])
	move_to(robot, static_positions['second_robot_on_tester1'])
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester1'])
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_home'])

def get_part_from_tester_2(robot):
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_over_tester2'])
	move_to(robot, static_positions['second_robot_on_tester2'])
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester2'])
	move_to(robot, static_positions['second_robot_middle_testers'])
	move_to(robot, static_positions['second_robot_home'])

def get_part_from_welder(robot):
	move_to(robot, static_positions['second_robot_ready_for_welder'])
	move_to(robot, static_positions['second_robot_over_welder'])
	move_to(robot, static_positions['second_robot_on_welder'])
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_welder'])
	move_to(robot, static_positions['second_robot_ready_for_welder'])
	move_to(robot, static_positions['second_robot_home'])

def connect_control(serial_port, baud_rate):
	ser = serial.Serial(serial_port, baud_rate, timeout=1)
	time.sleep(2)
	ser.reset_input_buffer()
	print('connected to control unit\n')
	return ser



control_port = '/dev/cu.usbmodem11201' #'/dev/ttyACM0'
comport = connect_control(control_port, 9600)

walle = connect_robot("192.168.0.101", 10000, 'walle')
roger = connect_robot("192.168.0.100", 10000, 'roger')

move_to(walle, static_positions['home'])
move_to(roger, static_positions['second_robot_home'])


while True:
    user_time_start = time.time()
    print('\nReady for next set')
    num_cycles = 50#int(input('How many valves to make: '))
    next = input('Press enter to continue')
    
    start = time.time()


	for i in range(num_cycles):
		print("getting part #: " + str(i) + '\n')
		put_part_into_welder_start_welder_and_get_next_part(walle, i, comport)
		get_part_from_welder(roger)
		if i % 2 == 1:
			put_part_into_tester_1(roger, comport)
			if i > 1:
				get_part_from_tester_2(roger)
				put_in_correct_output(roger, 1)
		else:
			put_part_into_tester_2(roger, comport)
			if i > 1:
				get_part_from_tester_1(roger)
				put_in_correct_output(roger, 1)


	end = time.time()
    print('the last: ' + str(num_cycles) + ' valves took: ' + str(end - start) + ' seconds for the robot to complete\n')
    print('and ' + str(start - user_time_start) + ' for the board flip and reload\n')
    print('total production time was: ' + str(end - user_time_start) + '\n')
    outfile = open('partslog.txt', 'a')
    outfile.write('50 @ time: ' + str(end) + ' total production time was: ' 
                    + str(end - user_time_start) + ' robot took: ' + str(end - start) 
                    + ' seconds and user took: ' + str(start - user_time_start) + '\n')
    outfile.close()


time.sleep(3)
disconnect_robot(walle)
disconnect_robot(roger)
sys.exit()
	




