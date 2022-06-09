import sys
import socket
import time
import serial
import threading
#prevents screen from sleeping
import caffeine
caffeine.on(display=True)

moves = {
    'home': 'MoveJoints(0,0,0,0,16.5,0)',
    'over_table': 'MovePose(44.273, 188.558, 182.037, -91.245, 39.824, 86.378)',
    #angular position equivelant [90.237,16.613,41.107,45.250,-64.991,-26.712]
    'on_table': 'MoveJoints(89.273, 26.844, 43.299, 41.055, -73.785, -17.312)',
    'over_solo1': 'MovePose(194.628, -4.558, 179.284, 92.036, 61.973, -94.366)',
    #angular position equivelant [12.032,17.799,41.078,44.851,-65.800,-23.951]
    'over_solo1_second_arm': 'MovePose(193.226, -118.732, 270.420, 86.820, 60.220, -87.570)',
    'over_solo2': 'MovePose(273.602, -22.689, 177.160, -111.630, 88.709, 107.607)',
    'over_solo3': 'MovePose(273.602, 35.201, 177.160, -111.630, 88.709, 107.607)',
    'on_solo1': 'MovePose(194.628, -4.558, 155.216, 92.036, 61.973, -94.366)',
    'on_solo1_second_arm': 'MovePose(193.226, -118.732, 242.670, 86.820, 60.220, -87.570)',
    'on_solo2': 'MovePose(273.602, -22.689, 152.715, -111.630, 88.709, 107.607)',
    'on_solo3': 'MovePose(273.602, 35.201, 152.760, -111.630, 88.709, 107.608)',
    'reject_solo1': 'MovePose(101.229, 19.675, 154.239, -179.391, 5.929, 163.172)',
    'reject_solo1_second_arm': 'MovePose(85.476, -173.104, 264.862, 143.183, 26.254, -120.841)',
    'reject_solo2': 'MovePose(266.048,91.651,154.362,-138.619,16.889,107.989)',
    'reject_solo3': 'MovePose(266.048,91.651,154.362,-138.619,16.889,107.989)',
    'pass_solo1': 'MoveJoints(0,0,0,0,16.5,0)',
    'pass_solo2': 'MovePose(24.851, 191.451, 93.762, -136.033, -4.021, 85.582)',
    'pass_solo3': 'MovePose(24.851, 191.451, 93.762, -136.033, -4.021, 85.582)',
}

#global state variables
#0 means empty, 1 means pass, and -1 means fail and 2 means currently testing
solo1_state = 0
solo2_state = 0
solo3_state = 0
part_ready = False
end = False

#log_file = open("log.txt","w+")
#log_file.close()
class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return

def my_callback(inp):
    global end
    #evaluate the keyboard input
    #print('You Entered:', inp, ' end status is:', end)
    if inp == 'x' or inp == 'X':
        end = True
        disconnect_robot(roger)
        disconnect_robot(walle)
        com.close()
        sys.exit()


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
        robot_socket_connection.send(bytes('SetJointVel(100)'+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to set joint velocity for robot at: ' + ip)
        return -1

    try:
        robot_socket_connection.send(bytes('MoveJoints(0,0,0,0,16.5,0)'+'\0','ascii'))
        response = robot_socket_connection.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to go to neutral position for robot at: ' + ip)
        return -1

    print('\n')
    return robot_socket_connection

def move_to(robot, position):
    global end
    try:
        robot.send(bytes(position+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        #print(response)
    except socket.error:
        print('Failed to move robot')
        end = True
    return 0

def open(robot):
    global end
    try:
        robot.send(bytes('gripperopen'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        robot.send(bytes('delay(0.1)'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        #print(response)
        time.sleep(.1)
    except socket.error:
        print('Failed to open gripper')
        end = True
        
def close(robot):
    global end
    try:
        robot.send(bytes('gripperclose'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        robot.send(bytes('delay(0.1)'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        #print(response)
        time.sleep(.1)
    except socket.error:
        print('Failed to close gripper')
        end = True

def disconnect_robot(robot):
    try:
        robot.send(bytes('DeactivateRobot'+'\0','ascii'))
        response = robot.recv(1024).decode('ascii')
        print(response) 
        robot.close() 
    except socket.error:
        print('Failed to disconnect') 

def connect_control(serial_port, baud_rate):
	ser = serial.Serial(serial_port, baud_rate, timeout=1)
	time.sleep(2)
	ser.reset_input_buffer()
	print('connected to control unit\n')
	return ser

def start_solo(com, n):
    com.write(n.encode())
    time.sleep(0.1)
    #line = com.readline()
    #string = line.strip().decode('utf-8')
    #if string == 'Received':
        #return 0
    #else:
        #return -1

#starts the solo test
def start_solo_1():
    start_solo(com, '1')

def start_solo_2():
    start_solo(com, '2')

def start_solo_3():
    start_solo(com, '3')

def check_for_update(com):
    global part_ready
    global solo1_state
    global solo2_state
    global solo3_state

    if com.in_waiting == 0:
        return False
    else:   
        print('total number of bytes left to read: ' + str(com.in_waiting))
        line = com.readline()
        info = line.strip().decode('utf-8')
        print(info)

        if info == "Table Home":
            part_ready = True
            return True
        if info == "Table Moving":
            part_ready = False
            return True
        if info == "1 Pass":
            solo1_state = 1
            return True
        if info == "2 Pass":
            solo2_state = 1
            return True
        if info == "3 Pass":
            solo3_state = 1
            return True
        if info == "1 Fail":
            solo1_state = -1
            return True
        if info == "2 Fail":
            solo2_state = -1
            return True
        if info == "3 Fail":
            solo3_state = -1
            return True

        return False


def print_status(line_no):
	print('from line #' + str(line_no))
	print("part_ready: " + str(part_ready))
	print("solo 1 ready: " + str(solo1_ready) + " solo 1 state: " + str(solo1_state))
	print("solo 2 ready: " + str(solo2_ready) + " solo 2 state: " + str(solo2_state))
	print("solo 3 ready: " + str(solo3_ready) + " solo 3 state: " + str(solo3_state))
	print('\n')

#goes from current position, gripperopen, to over_table, then on_table
#then gripperclose then over_table then to home
def get_valve_from_table(robot):
	move_to(robot, moves['over_table'])
	open(robot)
	move_to(robot, moves['on_table'])
	close(robot)
	move_to(robot, moves['over_table'])
	move_to(robot, moves['home'])

#goes from current position to over tester then into tester then gripperopen
#then over tester then back to home
def put_valve_into_solo_1(robot):
    move_to(robot, moves['over_solo1'])
    move_to(robot, moves['on_solo1'])
    open(robot)
    move_to(robot, moves['over_solo1'])
    move_to(robot, moves['home'])

def put_valve_into_solo_2(robot):
    move_to(robot, moves['over_solo2'])
    move_to(robot, moves['on_solo2'])
    open(robot)
    move_to(robot, moves['over_solo2'])
    move_to(robot, moves['home'])

def put_valve_into_solo_3(robot):
    move_to(robot, moves['over_solo3'])
    move_to(robot, moves['on_solo3'])
    open(robot)
    move_to(robot, moves['over_solo3'])
    move_to(robot, moves['home'])

#goes from current position to over tester then gripperopen then into tester then gripperclose
#then over tester then back to home
def get_valve_from_solo_1(robot):
    move_to(robot, moves['over_solo1'])
    open(robot)
    move_to(robot, moves['on_solo1'])
    close(robot)
    move_to(robot, moves['over_solo1'])
    move_to(robot, moves['home'])

def get_valve_from_solo_1_second_arm(robot):
    move_to(robot, moves['over_solo1_second_arm'])
    open(robot)
    move_to(robot, moves['on_solo1_second_arm'])
    close(robot)
    move_to(robot, moves['over_solo1_second_arm'])
    move_to(robot, moves['home'])

def get_valve_from_solo_2(robot):
    move_to(robot, moves['over_solo2'])
    open(robot)
    move_to(robot, moves['on_solo2'])
    close(robot)
    move_to(robot, moves['over_solo2'])
    move_to(robot, moves['home'])

def get_valve_from_solo_3(robot):
    move_to(robot, moves['over_solo3'])
    open(robot)
    move_to(robot, moves['on_solo3'])
    close(robot)
    move_to(robot, moves['over_solo3'])
    move_to(robot, moves['home'])

#from current position to reject then gripperopen
#then back to home
def put_valve_into_reject_1(robot):
    move_to(robot, moves['reject_solo1'])
    open(robot)
    move_to(robot, moves['home'])

def put_valve_into_reject_1_second_arm(robot):
    move_to(robot, moves['reject_solo1_second_arm'])
    open(robot)
    move_to(robot, moves['home'])

def put_valve_into_reject_2(robot):
    move_to(robot, moves['reject_solo2'])
    open(robot)
    move_to(robot, moves['home'])

def put_valve_into_reject_3(robot):
    move_to(robot, moves['reject_solo3'])
    open(robot)
    move_to(robot, moves['home'])

#from current position to bin then gripperopen
#then back to home 
def put_valve_into_output_bin(robot):
    move_to(robot, moves['pass_solo3'])
    open(robot)
    move_to(robot, moves['home'])

kthread = KeyboardThread(my_callback)

#log_file.write("started the keyboard close signal monitor\n")

com = connect_control('/dev/cu.usbmodem1101', 9600)
roger = connect_robot("192.168.0.100", 10000, 'roger')
walle = connect_robot("192.168.0.101", 10000, 'walle')
#roger = connect_robot("127.0.0.1", 65432, 'roger')
#walle = connect_robot("127.0.0.1", 65433, 'walle')

com.reset_input_buffer()

if roger == -1 or walle == -1:
    print('failed connection, exiting')
    disconnect_robot(roger)
    disconnect_robot(walle)
    com.close()
    sys.exit()

while True:
    if end:
        break

    if check_for_update(com):

        if solo3_state == 1:
            get_valve_from_solo_3(walle)
            put_valve_into_output_bin(walle)
            solo3_state = 0
            continue

        if solo3_state == -1:
            get_valve_from_solo_3(walle)
            put_valve_into_reject_3(walle)
            solo3_state = 0
            continue

        if solo2_state == 1:
            get_valve_from_solo_2(walle)
            put_valve_into_output_bin(walle)
            solo2_state = 0
            continue

        if solo2_state == -1:
            get_valve_from_solo_2(walle)
            put_valve_into_reject_2(walle)
            solo2_state = 0
            continue

        if solo1_state == 1:
            get_valve_from_solo_1_second_arm(walle)
            solo1_state = 0
            if solo2_state == 0:
                put_valve_into_solo_2(walle)
                solo2_state = 2
                start_solo_2()
                continue

            if solo3_state == 0:
                put_valve_into_solo_3(walle)
                solo3_state = 2
                start_solo_3()
                continue

        if solo1_state == -1:
            get_valve_from_solo_1(roger)
            solo1_state = 0
            put_valve_into_reject_1(roger)
            continue

        if part_ready:
            get_valve_from_table(roger)
            part_ready = False
            if solo1_state == 0:
                put_valve_into_solo_1(roger)
                solo1_state = 2
                start_solo_1()
                continue
            else:
                put_valve_into_reject_1(roger)
                continue

#disconnect_robot(roger)
#disconnect_robot(walle)
sys.exit()


