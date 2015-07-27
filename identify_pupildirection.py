'''
	Copy right: Zhitao Zhang (zzt124@uw.edu)
	This script receive data from pupil server
	and determite which direction the pupil is looking at.
'''

import zmq
import math
import signal

from sys import stdin, exit

def signal_handler(signal, frame):
	print 'Exiting the program right now'
	exit(0)

def det_direction(confidence, norm_pos, con_level):
	'''
		Determite which direction the user
		is looking at
	'''
	# For x, y if the position is within [0.4, 0.7],
	# eye would't be considered as looking at specific
	# direction
	if confidence > con_level:
		# case: confidence is large enough for consideration
		norm_x, norm_y = map(float, norm_pos[1:-1].split(','))
		if norm_x > 0.7:
			# case 1: eye is looking at rigth side
			if norm_y < 0.4:
				print 'SE'
			elif norm_y > 0.7:
				print 'NE'
			else:
				print 'E'
		elif norm_x < 0.4:
			# case 2: eye is looking at left side
			if norm_y < 0.4:
				print 'SW'
			elif norm_y > 0.7:
				print 'NW'
			else:
				print 'W'
		else:
			# case 3: eye is looking at middle part
			if norm_y < 0.4:
				print 'S'
			elif norm_y > 0.7:
				print 'N'
			else:
				pass
	else:
		# confidence is too small to make a decision
		pass


def main():

	# lowest acceptant level
	con_level = 0.65

	# network setup connection with pupil eye tracker
	port = raw_input('Please enter port number: ')
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	# interpret ip address as string
	ip_addr = raw_input("Enter the ip address for PUpil Server: ")
	# whole ip address
	socket.connect('%s:%s' % (ip_addr, port))


	# filter message by stating string "String", '' receives all messages
	socket.setsockopt(zmq.SUBSCRIBE, '')

	# accepting connection from pupil head set
	while True:
		msg = socket.recv()

		items = msg.split("\n")
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check the message type, if the message is from 
		if msg_type == 'Pupil':
			try:
				# extract confidence level of pupil position
				confidence = float(items['confidence'])
				# norm_pos is a attribute in the dictionary as string
				norm_pos = items['norm_pos']

				det_direction(confidence, norm_pos, con_level)
			except KeyError:
				pass
		else:
			# pass on other messages not related to pupil position
			pass

if __name__ == "__main__":
	main()
	signal.signal(signal.SIGINT, signal_handler)

