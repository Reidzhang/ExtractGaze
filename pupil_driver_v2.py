'''
	Copy right: Zhitao Zhang (zzt124@uw.edu)
	This script is a seconde version of sphero
	driver using pupil headset.
	The way to drive it is drawing path for sphero
	with gaze points
'''

import zmq
import math
import sphero_driver
import numpy as np
import signal
import time
import matplotlib.pyplot as plt
from sys import stdin, exit

sphero = sphero_driver.Sphero()

def signal_handler(signal, frame):
	print 'Exiting the program right now'
	sphero.set_back_led(0, False)
	sphero.disconnect();
	exit(0)

def det_angle(start_point, end_point):
	'''
	Determine angle difference between two points
	'''
	x_diff = end_point[0] - start_point[0]
	y_diff = end_point[1] - start_point[1]
	# calculate hypotenuse
	hypotenuse = math.sqrt(x_diff ** 2 +  y_diff ** 2)
	tmp_angle = math.degrees(math.asin(x_diff / hypotenuse))
	if tmp_angle >= 0:
		if y_diff >= 0:
			return tmp_angle
		else:
			return 180 - tmp_angle
	else:
		# tmp_angle less than 0
		if y_diff > 0:
			return 359 + tmp_angle
		else:
			return 180 - tmp_angle

def process_data(*args):
	start_point = args[0]
	start_point_ts = args[1]
	end_point = args[2]
	end_point_ts = args[3]
	if end_point_ts - start_point_ts < 0.2:
		return start_point, start_point_ts
	else:
		angle = det_angle(start_point, end_point)
		x_diff = abs(start_point[0] - end_point[0])
		y_diff = abs(start_point[1] - end_point[1])
		x_diff *= 1920
		y_diff *= 1080
		travel_pixel = math.sqrt(math.pow(x_diff, 2) + math.pow(y_diff, 2))
		# set 1 pixel in screen is equal to 2 cm in real world
		travel_distance = travel_pixel * 2.
		# with speed = 50, sphero travel distance is around 66 cm
		count = math.ceil(travel_distance / 66)
		i = 0
		while i <= count and travel_pixel > 6:
			sphero.roll(50, int(angle), 1, False)
			i += 1
		return end_point, end_point_ts

def receive_pupil_data(socket, con_level):
	# set one pixel values equals to 2 cm in real world
	pixel =  2.
	# set an start point and its timestamp
	start_point = None
	start_point_ts = None
	# accepting connection from pupil head set
	while True:
		msg = socket.recv()
		items = msg.split('\n')
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check of Gaze type message
		if msg_type == 'Gaze':
			try:
				confidence = float(items['confidence'])
				
				if confidence > con_level:
					timestamp = float(items['timestamp'])
					# norm_pos is a attribute in the dictionary as string
					norm_pos = items['norm_pos']
					norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
					if start_point == None:
						start_point = norm_x,norm_y
						start_point_ts = timestamp 
					else:
						# case it isn't a start point
						# there is an end point for this path
						end_point = norm_x, norm_y
						args = [start_point, start_point_ts, end_point, timestamp]
						start_point, start_point_ts = process_data(*args)
			except KeyError:
				pass
		else:
			# pass on other messages not related to pupil position
			pass

def make_calibration(socket):
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
		print items
		if msg_type == 'Pupil':
			try:
				norm_pos = items['norm_pos']
				norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
				if norm_x == 0 and norm_y == 0:
					msg_count += 1;
				else:
					msg_count = 0
			except KeyError:
				pass
		# check the msg_count
		if msg_count == 0:
			sphero.roll(0, 6, 1, False)
			time.sleep(0.3)
			sphero.set_heading(0, False)
		elif msg_count >= 30:
			calibrated = True
		else:
			pass


def main():

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
	make_calibration(socket)
	# set lowest acceptence level to be 65% 
	receive_pupil_data(socket, con_level = 0.65)


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
	signal.signal(signal.SIGINT, signal_handler)
	main()

