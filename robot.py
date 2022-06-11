import sys
import socket
import time
import serial
import threading
from datetime import date


x_adj = 0
y_adj = 0
z_adj = 0

tester_1_pass_or_fail = 12
tester_2_pass_or_fail = 12


delay_set = True

estop_pressed = 0

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

print("Today's date:", date.today())
set_default_speed = 100
#set_slow_speed = int(input('Slow speed: '))
part_type_info = str(input('Enter the product name: '))
output_file_descriptor1 = str(input('Enter the MO #: '))
output_file_descriptor2 = str(input('Enter the Lot #: '))
date_info_today = date.today()

default_speed = 'SetJointVel(' + str(set_default_speed) + ')'
slower_pickup_speed = 'SetJointVel(' + str(set_default_speed) + ')'

def generate_nth_position(i, z_increase):
	#position 50 (i = 49) 
	#on part: [-123.077,291.225,103.731,-92.322,0.916,89.977]
	#over part: [-123.077,291.225,157.156,-92.322,0.916,89.977]

	dist_between_parts = 27.719
	start_pos_x = 125.703 + x_adj
	start_pos_y = 176.158 + y_adj
	start_pos_z = 95.115 + z_adj   #70.729 this used to be 105.115 before
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
	print('Attempting to connect to robot: ' + name_of_robot + ' at address: ' + ip + ' over port: ' + str(port) + '\n...')
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

	print('Sending wake command...')
	try:
		robot_socket_connection.send(bytes('ActivateRobot'+'\0','ascii'))
		if delay_set == True:
			for i in range(15):
				time.sleep(1)
				print('...')
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
		robot_socket_connection.send(bytes('ResetError'+'\0','ascii'))
		robot_socket_connection.send(bytes('ClearMotion'+'\0','ascii'))
		robot_socket_connection.send(bytes('ResumeMotion'+'\0','ascii'))
		#robot_socket_connection.send(bytes('PauseMotion'+'\0','ascii'))
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

def move_to(robot, position, comport):
	get_serial_status(comport)
	#check estop
	  #   while comport.in_waiting:
			# line = comport.readline()
			# info = line.strip().decode('utf-8')
			# print(info)
			# if info == "1 Pass":
			# 	tester_1_pass_or_fail = 1
			# elif info == "1 Fail":
			# 	tester_1_pass_or_fail = 0
			# elif info == "2 Pass":
			# 	tester_2_pass_or_fail = 1
			# elif info == "2 Fail":
			# 	tester_2_pass_or_fail = 0
	try:
		robot.send(bytes(position+'\0','ascii'))
		#response = robot.recv(1024).decode('ascii')
		#print(response)
	except socket.error:
		print('Failed to move robot, exiting...')
		sys.exit()
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
	global tester_1_pass_or_fail
	global tester_2_pass_or_fail
	global estop_pressed
	if i == 0:
		open_gripper(robot)
		move_to(robot, generate_nth_position(i, 100), comport)
		#time.sleep(0.1)
		move_to(robot, generate_nth_position(i, 0), comport)
		close_gripper(robot)
		move_to(robot, generate_nth_position(i, 100), comport)
		move_to(robot, static_positions['home'], comport)

	move_to(robot, static_positions['ready_for_welder'], comport)
	move_to(robot, static_positions['over_welder'], comport)
	move_to(robot, static_positions['on_welder'], comport)
	open_gripper(robot)
	move_to(robot, static_positions['over_welder'], comport)
	move_to(robot, static_positions['ready_for_welder'], comport)

	comport.write('W'.encode())

	move_to(robot, static_positions['home'], comport)

	if i < 49:
		move_to(robot, generate_nth_position(i+1, 100), comport)
		#time.sleep(0.1)
		move_to(robot, generate_nth_position(i+1, 0), comport)
		close_gripper(robot)
		move_to(robot, generate_nth_position(i+1, 100), comport)
		move_to(robot, static_positions['home'], comport)

	while True:
		if comport.in_waiting:
			line = comport.readline()
			info = line.strip().decode('utf-8')
			if info == "Welder Home":
				if estop_pressed == 0:
					break
				else:
					get_serial_status(comport)
					break
			elif info == "1 Pass":
				tester_1_pass_or_fail = 1
			elif info == "1 Fail":
				tester_1_pass_or_fail = 0
			elif info == "2 Pass":
				tester_2_pass_or_fail = 1
			elif info == "2 Fail":
				tester_2_pass_or_fail = 0
			elif info == "Estop":
				try:
					estop_pressed = 1
					walle.send(bytes('PauseMotion'+'\0','ascii'))
					roger.send(bytes('PauseMotion'+'\0','ascii'))
					outfile = open(log_file_name_and_location, 'a')
					outfile.write('E-Stop pressed at: ' + str(time.time()) + '\n')
					outfile.close()
					#response = robot.recv(1024).decode('ascii')
					#print(response)
					#time.sleep(.1)
				except socket.error:
					print('Failed to open gripper')
			elif info == "Estart":
				try:
					estop_pressed = 0
					walle.send(bytes('ResumeMotion'+'\0','ascii'))
					roger.send(bytes('ResumeMotion'+'\0','ascii'))
					outfile = open(log_file_name_and_location, 'a')
					outfile.write('E-Stop reset at: ' + str(time.time()) + '\n')
					outfile.close()
					#response = robot.recv(1024).decode('ascii')
					#print(response)
					#time.sleep(.1)
				except socket.error:
					print('Failed to open gripper')

		time.sleep(0.05)

def put_part_into_tester_1(robot, comport):
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_over_tester1'], comport)
	move_to(robot, static_positions['second_robot_on_tester1'], comport)
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester1'], comport)
	comport.write('2'.encode())
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_home'], comport)

def put_part_into_tester_2(robot, comport):
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_over_tester2'], comport)
	move_to(robot, static_positions['second_robot_on_tester2'], comport)
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester2'], comport)
	comport.write('1'.encode())
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_home'], comport)

def put_in_correct_output(robot, pass_or_fail_value, i_val):
	if pass_or_fail_value == 1:
		move_to(robot, static_positions['second_robot_good_output'], comport)
	else: #if pass_or_fail_value == 0:
		outfile = open(log_file_name_and_location, 'a')
		outfile.write('Part #' + str(i_val) + ' was bad')
		outfile.close()
		move_to(robot, static_positions['second_robot_bad_output'], comport)
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_home'], comport)

def get_part_from_tester_1(robot):
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_over_tester1'], comport)
	move_to(robot, static_positions['second_robot_on_tester1'], comport)
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester1'], comport)
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_home'], comport)

def get_part_from_tester_2(robot):
	open_gripper(robot)
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_over_tester2'], comport)
	move_to(robot, static_positions['second_robot_on_tester2'], comport)
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_tester2'], comport)
	move_to(robot, static_positions['second_robot_middle_testers'], comport)
	move_to(robot, static_positions['second_robot_home'], comport)

def get_part_from_welder(robot):
	move_to(robot, static_positions['second_robot_ready_for_welder'], comport)
	move_to(robot, static_positions['second_robot_over_welder'], comport)
	move_to(robot, static_positions['second_robot_on_welder'], comport)
	close_gripper(robot)
	move_to(robot, static_positions['second_robot_over_welder'], comport)
	move_to(robot, static_positions['second_robot_ready_for_welder'], comport)
	move_to(robot, static_positions['second_robot_home'], comport)

def connect_control(serial_port, baud_rate):
	ser = serial.Serial(serial_port, baud_rate, timeout=1)
	for i in range(15):
		time.sleep(1)
		print('...')
	ser.reset_input_buffer()
	print('connected to control unit\n')
	return ser

def get_serial_status(comport):
	global tester_1_pass_or_fail
	global tester_2_pass_or_fail
	global estop_pressed
	while comport.in_waiting or estop_pressed == 1:
		if not comport.in_waiting:
			continue
		line = comport.readline()
		info = line.strip().decode('utf-8')
		print(info)
		if info == "1 Pass":
			tester_1_pass_or_fail = 1
		elif info == "1 Fail":
			tester_1_pass_or_fail = 0
		elif info == "2 Pass":
			tester_2_pass_or_fail = 1
		elif info == "2 Fail":
			tester_2_pass_or_fail = 0
		elif info == "Estop":
			try:
				estop_pressed = 1
				walle.send(bytes('PauseMotion'+'\0','ascii'))
				roger.send(bytes('PauseMotion'+'\0','ascii'))
				outfile = open(log_file_name_and_location, 'a')
				outfile.write('E-Stop pressed at: ' + str(time.time()) + '\n')
				outfile.close()
				#response = robot.recv(1024).decode('ascii')
				#print(response)
				#time.sleep(.1)
			except socket.error:
				print('Failed to open gripper')
		elif info == "Estart":
			try:
				estop_pressed = 0
				walle.send(bytes('ResumeMotion'+'\0','ascii'))
				roger.send(bytes('ResumeMotion'+'\0','ascii'))
				outfile = open(log_file_name_and_location, 'a')
				outfile.write('E-Stop reset at: ' + str(time.time()) + '\n')
				outfile.close()
				#response = robot.recv(1024).decode('ascii')
				#print(response)
				#time.sleep(.1)
			except socket.error:
				print('Failed to open gripper')

		
			


control_port = '/dev/ttyACM0'
comport = connect_control(control_port, 9600)

walle = connect_robot("192.168.0.101", 10000, 'walle')
roger = connect_robot("192.168.0.100", 10000, 'roger')

move_to(walle, static_positions['home'], comport)
move_to(roger, static_positions['second_robot_home'], comport)

log_file_name_and_location = 'Desktop/' + part_type_info + '_MO' + output_file_descriptor1 + '_LOT' + output_file_descriptor2 + '_DATE' + str(date_info_today) + '_partslog.txt'

first_run_start_up = 1

while True:
	user_time_start = time.time()
	if first_run_start_up == 1:
		first_run_start_up = 0
		print('\nReady for next set')
		num_cycles = 50#int(input('How many valves to make: '))
		next = input('Press enter to continue')
		start = time.time()
		comport.reset_input_buffer()
		outfile = open(log_file_name_and_location, 'a')
		outfile.write('Product Name: ' + part_type_info + ' Manufacturing Order Number: ' + output_file_descriptor1 + ' Lot Number: ' + output_file_descriptor2 + '\n')
		outfile.write('Production started: ' + str(date_info_today) + ' at time: ' + str(start) + '\n' + '\n')
		outfile.close()
	else:
		comport.write('A'.encode())
		print('\nReady for next set')
		num_cycles = 50#int(input('How many valves to make: '))
		next = input('Press enter to continue')
		start = time.time()
		comport.reset_input_buffer()
		
		outfile = open(log_file_name_and_location, 'a')
		outfile.write('Product Name: ' + part_type + ' Manufacturing Order Number: ' + output_file_descriptor1 + ' Lot Number: ' + output_file_descriptor2 + '\n')
		outfile.write('Production started: ' + str(date_info_today) + ' at time: ' + str(start) + '\n' + '\n')
		outfile.close()
		comport.write('B'.encode())

	for i in range(num_cycles):
		print("getting part #: " + str(i) + '\n')
		get_serial_status(comport)
		put_part_into_welder_start_welder_and_get_next_part(walle, i, comport)
		if i % 2 == 1:
			if i > 1:
				while tester_1_pass_or_fail == 12:
					get_serial_status(comport)
				get_part_from_tester_1(roger)
				put_in_correct_output(roger, tester_1_pass_or_fail, i)
				tester_1_pass_or_fail = 12

			get_part_from_welder(roger)
			put_part_into_tester_1(roger, comport)

		else:
			if i > 1:
				while tester_2_pass_or_fail == 12:
					get_serial_status(comport)
				get_part_from_tester_2(roger)
				put_in_correct_output(roger, tester_2_pass_or_fail, i)
				tester_2_pass_or_fail = 12

			get_part_from_welder(roger)
			put_part_into_tester_2(roger, comport)


	end = time.time()
	print('the last: ' + str(num_cycles) + ' valves took: ' + str(end - start) + ' seconds for the robot to complete\n')
	print('and ' + str(start - user_time_start) + ' for the board flip and reload\n')
	print('total production time was: ' + str(end - user_time_start) + '\n')
	outfile = open(log_file_name_and_location, 'a')
	outfile.write('50 @ time: ' + str(end) + ' total production time was: ' 
		+ str(end - user_time_start) + ' robot took: ' + str(end - start) 
		+ ' seconds and user took: ' + str(start - user_time_start) + '\n')
	outfile.close()


time.sleep(3)
disconnect_robot(walle)
disconnect_robot(roger)
sys.exit()
	



