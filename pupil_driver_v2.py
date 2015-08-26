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
		if y_diff >= 0:
			return 359 - tmp_angle
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
		resolution = (travel_pixel * 2.) / (7.366 * 3.14)
		wait_time = resolution / 3.9
		sphero.roll(100, angle, 1, False)
		time.sleep(wait_time)
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
		items = dict([ i.split(':', 1) for i in itmes[: -1] ])
		# check of Gaze type message
		if msg_type == 'Gaze':
			try:
				confidence = float(items['confidence'])
				
				if confidence > con_level:
					timestamp = float(items['timestamp'])
					# norm_pos is a attribute in the dictionary as string
					norm_pos = items['norm_pos']
					norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
					if start_point = None:
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
	receive_pupil_data(socket, con_level)


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

