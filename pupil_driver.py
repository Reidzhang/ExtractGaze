'''
	Copy right: Zhitao Zhang (zzt124@uw.edu)
	This script is a driver module using pupil
	headset for sphero.

	Pupil driver uses ZeroMQ, the smart socket library to receive
	feedback messages from pupil servers with Publish-Subscribe
	patterns.
	You can find more infomation using this link:
	http://zeromq.org
'''

import zmq
import math
import signal
import sphero_driver
import time
import matplotlib.pyplot as plt
import numpy as np
from sys import stdin, exit


sphero = sphero_driver.Sphero();

def signal_handler(signal, frame):
	print 'Exiting the program right now'
	sphero.set_back_led(0, False)
	sphero.disconnect();
	exit(0)

def det_angle(confidence, norm_pos, con_level, data_range):
	'''
		Determite which angle the user
		is looking at. By the definition of sphero.
        0 degree is going forward. So in y direction
        it is considered as 0 degree. The minimum is 0
        degree. The maximum is 359 degree.
	'''
	middle_x = data_range[0]
	middle_y = data_range[1]
	inner_radius = data_range[2]
	if confidence > con_level:
		# case: confidence is large enough for consideration
		norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
		# flip the x axis
		norm_x = 1 - norm_x
		diff_x = norm_x - middle_x
		diff_y = norm_y - middle_y
		# calculate hypotenuse
		hypotenuse = math.sqrt(diff_x ** 2 + diff_y ** 2)
		if hypotenuse < inner_radius:
			return None
		else:
			angle = 0.0
			if (diff_x > 0 and diff_y >= 0):
				# first quadrant
				angle = 90 - math.degrees(math.asin(diff_y / hypotenuse))
			elif (diff_x <= 0 and diff_y >= 0):
				# second quadrant
				angle = 270 + math.degrees(math.asin(diff_y / hypotenuse))
			elif (diff_x < 0  and diff_y <= 0):
				# third quadrant
				angle = 180 - math.degrees(math.asin(diff_y / hypotenuse))
			else:
				# fourth quadrant
				angle = 90 - math.degrees(math.asin(diff_y / hypotenuse))
			return angle
	else:
		# confidence is too small to make a decision
		return None;

def make_calibration(socket, con_level, data_range):
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
		# pupil infomation
		if msg_type == 'Pupil':
			try:
				# extract confidence level of pupil position
				confidence = float(items['confidence'])
				norm_pos = items['norm_pos']
				pupil_angle = det_angle(confidence, norm_pos, con_level, data_range)
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

def collect_data(socket, con_level):
	# Helper function for collecting data of pupil
	# positions in different regions
	ret = []
	count = 0
	while count < 350:
		msg = socket.recv()
		items = msg.split('\n')
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check the message type
		if msg_type == 'Pupil':
			try:
				# check confident level of pupil position
				confidence = float(items['confidence'])
				norm_pos = items['norm_pos']
				if confidence > con_level:
					norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
					norm_x = 1 - norm_x
					data_pt = norm_x, norm_y
					ret.append(data_pt)
					count += 1
			except KeyError:
				pass
	return ret


def space_calibration(socket, con_level):
	'''
	Let the user to look at top left, top right, bottom left, and bottom right
	four extreme points. Through these four points to decide the observation
	region
	'''
	inter_socket = socket
	print "Please look at four extreme region(top_left, top_right, bottom_left"
	print "and bottom_right) with your pupil."
	print "Beging collecting data......."
	pt_cloud = collect_data(inter_socket, con_level)
	print "Finished data collecting"
	# convert data into np array
	data_pt_cloud = np.array(pt_cloud)
	# convert to X and Y
	X = data_pt_cloud[:,0]
	Y = data_pt_cloud[:,1]
	plt.scatter(X, Y)
	plt.show()
	# get the min and max for X and Y
	x_min = np.amin(X)
	x_max = np.amax(X)
	y_min = np.amin(Y)
	y_max = np.amax(Y)
	middle_x = (x_min + x_max) / 2.
	middle_y = (y_min + y_max) / 2.
	x_range = abs(x_min - x_max)
	y_range = abs(y_min - y_max)
	t_range = min(x_range, y_range)
	return middle_x, middle_y, (t_range/4.)

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

	# find the middle point and get the range
	middle_x, middle_y, inner_radius = space_calibration(socket, con_level)
	data_range = [middle_x, middle_y, inner_radius]
	# Beging calibration process
	make_calibration(socket, con_level, data_range)
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
				heading = det_angle(confidence, norm_pos, con_level, data_range)
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
