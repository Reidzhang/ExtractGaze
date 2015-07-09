"""
Receive data from Pupil server broadcast for TCP
test script to see what the stream looks like and for
debugging

"""
'''
	Copy right Zhitao Zhang
	Add new feature with 
'''
import zmq
import math

# Network set up
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:" + port)
# filter by message by stating string "STRING", '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, '')
# reference surface we are going to track
surface_name = 'nexus'
# error message constant
error_message = 'Error occur in extracing gaze posiiton'

# lowest acceptant level
con_level = 0.65
# resolution of nexus
y_pixel = 1200
x_pixel = 1920
# minimal radius is 10 pixels
radius = 5
# time check is two seconds
duration = 2

# Setup three global variables, x, y and timestamp. So we can compare different between
# those messages
x = -1.0
y = -1.0
timestamp = -1

# set up the global value for printing message
command_out = 'adb shell input tap {} {}'
# dictionary key
key = 'realtime gaze on nexus'

while True:
	msg = socket.recv()

	items = msg.split("\n")
	msg_type = items.pop(0)
	items = dict([i.split(':', 1) for i in items[: -1] ])
	# check the message type, if the message is from gaze
	if msg_type == 'Gaze':
		try:
			# extract confidence and timestamp
			confidence = float(items['confidence'])
			temp_timestamp = float(items['timestamp'])
			if (confidence > con_level and key in items):
				gp = items[key]
				# Check the confidence level then check two gp with timestamp.
				gp_x, gp_y = map(float, gp[1:-1].split(','))
				if (0 <= gp_x <= 1 and 0 <= gp_y <= 1):
					# denormalized the x and y position with pixel
					# values in the reference surface
					temp_x = gp_x * x_pixel
					temp_y = (1 - gp_y) * y_pixel
					print 'x: {}, y: {}, timestamp: {}'.format(x, y, timestamp)
					print 'temp_x: {}, temp_y: {}, temp_timestamp: {}'.format(temp_x, temp_y, temp_timestamp)
					if x == -1.0 or y == -1.0:
						# case: get new x and y
						x = temp_x
						y = temp_y
						timestamp = temp_timestamp
					else:
						# computation on checking the difference and timestamp
						x_diff = abs(x - temp_x)
						y_diff = abs(y - temp_y)
						distance = math.sqrt((x_diff ** 2) + (y_diff ** 2))
						if distance < radius:
							# case: new gaze location is within range of
							# standard point of gaze_location
							if (temp_timestamp - timestamp) > duration:
								# need to change to write to bash file
								print command_out.format(x, y)
								x = -1.0
								y = -1.0
								timestamp = -1.0
						else:
							# case: new gaze locataion is outside range
							# replace the standard point to new gaze_location
							x = temp_x
							y = temp_y
							timestamp = temp_timestamp
					# if x == -1.0 or y == -1.0:
					# 	# case: get new x and y
					# 	x = temp_x
					# 	y = temp_y
					# 	timestamp = temp_timestamp
					# else:
					# 	# computation on checking the difference and timestamp
					# 	x_diff = abs(x - temp_x)
					# 	y_diff = abs(y - temp_y)
					# 	distance = math.sqrt((x_diff**2) + (y_diff**2))
					# 	if (distance < radius and abs(timestamp - temp_timestamp) > duration):
					# 		# need to change to write to bash file, using
					# 		# os.write, os.open, os.close
					# 		print command_out.format(x, y)
					# 	# replace the old x, y and timestamp with new value
					# 	x = temp_x
					# 	y = temp_y
					# 	timestamp = temp_timestamp
			else:
				# case: confidence less than lowest confident level
				pass
		except KeyError:
			print error_message
			break
	else:
		# pass on other messages not related to gaze position
		pass
