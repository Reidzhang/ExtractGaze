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

def main():
	# network setup connection with pupil eye tracker
	port = '5000'
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	ip_addr = input("Enter the ip address for pupil tracker: ")
	socket.connnect(ip_addr + port)


	# filter message by stating string "String", '' receives all messages
	socket.setsockopt(zmq.SUBSCRIBE, '')

	# accepting connection from pupil head set
	while True:
		msg = socket.recv()

		items = msg.split("\n")
		msg_type = items.pop(0)
		items = dict([ i.split(':', 1) for i in items[: -1] ])
		# check the message type, if the message is from 
		if msg_type == 'pupil':
			try:
				print items
			except KeyError:
				pass
		else:
			# pass on other messages not related to pupil position
			pass

if __name__ == "__main__":
	main()
	signal.signal(signal.SIGINT, signal_handler)
	
