'''
	Copy right: Zhitao Zhang (zzt124@uw.edu)
	This script receive data from pupil server
	and determite which direction the pupil is looking at.
'''

import zmq
import math
import signal
import sphero_driver
import time
from sys import stdin, exit

sphero = sphero_driver.Sphero();

org_x = 0.5
org_y = 0.5
inner_radius = 0.10
out_radius = math.sqrt(0.5**2 + 0.5**2)

def signal_handler(signal, frame):
	print 'Exiting the program right now'
	sphero.set_back_led(0, False)
	sphero.disconnect();
	exit(0)

def det_angle(confidence, norm_pos, con_level):
	'''
		Determite which angle the user
		is looking at. By the definition of sphero.
        0 degree is going forward. So in y direction
        it is considered as 0 degree.
	'''
	# For x, y if the position is within [0.4, 0.6],
	# eye would't be considered as looking at specific
	# angle
	if confidence > con_level:
		# case: confidence is large enough for consideration
		norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
		diff_x = norm_x - org_x
		diff_y = norm_y - org_y
		# calculate hypotenuse
		hypotenuse = math.sqrt(diff_x ** 2 + diff_y ** 2)
		if hypotenuse < inner_radius:
			return None
		else:
			angle = 0.0
			if (diff_x > 0 and diff_y >= 0):
				# first quadrant
				angle = 270 + math.degrees(math.asin(diff_y / hypotenuse))
			elif (diff_x <= 0 and diff_y >= 0):
				# second quadrant
				angle = 90 - math.degrees(math.asin(diff_y / hypotenuse))
			elif (diff_x < 0  and diff_y <= 0):
				# third quadrant
				angle = 90 - math.degrees(math.asin(diff_y / hypotenuse))
			else:
				# fourth quadrant
				angle = 180 - math.degrees(math.asin(diff_y / hypotenuse))
			return angle
	else:
		# confidence is too small to make a decision
		return None;

def make_calibration(socket, con_level):
	'''
		Calibrate Sphero at the beginning of
		the process. Make the heading related to
		the user
	'''
	calibrated = False
	msg_count = 0
	sphero.set_back_led(255, False)
	while calibrated != True:
		msg = socket.recv()
		items = msg.split("\n")
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check the message type, if the message is from
		# Gaze infomation
		if msg_type == 'Gaze':
			try:
				# extract confidence level of pupil position
				confidence = float(items['confidence'])
				norm_pos = items['norm_pos']
				pupil_angle = det_angle(confidence, norm_pos, con_level)
				if pupil_angle > 135 and pupil_angle < 225:
					msg_count += 1;
				else:
					msg_count = 0
			except KeyError:
				pass
		# check the msg_count
		if msg_count == 0:
			sphero.roll(0, 6, 1, False)
			time.sleep(0.2)
			sphero.set_heading(0, False)
		elif msg_count >= 31:
			calibrated = True
		else:
			pass
	sphero.set_back_led(0, False)
	sphero.set_rgb_led(0, 0, 255, 0, False)


def main():

	# lowest acceptant level
	con_level = 0.65

	# network setup connection with pupil eye tracker
	port = raw_input('Please enter port number: ')
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	# interpret ip address as string
	ip_addr = raw_input("Enter the ip address for Pupil Server: ")
	# whole ip address
	socket.connect('%s:%s' % (ip_addr, port))
	# filter message by stating string "String", '' receives all messages
	socket.setsockopt(zmq.SUBSCRIBE, '')

	# Beging calibration process
	make_calibration(socket, con_level)
	# set up speed
	speed = 100

	# accepting connection from pupil head set
	while True:
		msg = socket.recv()

		items = msg.split("\n")
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check the message type, if the message is from 
		# Gaze type
		if msg_type == 'Pupil':
			try:
				# extract confidence level of pupil position
				confidence = float(items['confidence'])
				# norm_pos is a attribute in the dictionary as string
				norm_pos = items['norm_pos']
				heading = det_angle(confidence, norm_pos, con_level)
				if heading == None:
					sphero.roll(speed, 0, 0, False);
				else:
					sphero.roll(speed, int(round(heading)), 1, False);
			except KeyError:
				pass
		else:
			# pass on other messages not related to pupil position
			pass

if __name__ == "__main__":
	# general set-up of sphero
	# set up sphero connection
	sphero.connect();
	# abstract from mannually set up sphero
	sphero.set_raw_data_strm(40, 1, 0, False)
	# time slepp
	time.sleep(1);
	# set up LED light for reminder
	sphero.set_rgb_led(255,0,0,0,False)
	time.sleep(1)
	sphero.set_rgb_led(0,255,0,0,False)
	time.sleep(1)
	sphero.set_rgb_led(0,0,255,0,False)
	time.sleep(1)
	sphero.set_rgb_led(0,0,0,0,False)
	sphero.set_stablization(1, False)
	main()
	signal.signal(signal.SIGINT, signal_handler)
