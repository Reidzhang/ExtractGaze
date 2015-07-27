"""
Receive data from Pupil server broadcast for TCP
test script to see what the stream looks like and for
debugging
"""
'''
	Copy right: Zhitao Zhang(zzt124@uw.edu)
	Receive data from Pupol Server broadcast using TCP/IP
	connection and establish an connection with Android devices
	sending shell_command for clicking.

	This is an inital design. Will need some improvement later.

	For using adb establishing connection, you need to install
	pyadb first.
'''
import zmq
import math
import signal
from pyadb import ADB
from sys import stdin, exit

adb = ADB()

def signal_handler(signal, frame):
	adb.kill_server()
	exit(0)

def main():

	# reference surface we are going to track
	surface_name = 'nexus'
	# error message constant
	error_message = 'Error occur in extracing gaze locataion'

	# lowest acceptant level
	con_level = 0.65

	# resolution of nexus
	y_pixel = 1200
	x_pixel = 1920

	# minimal radius for the range of the
	# gaze location
	radius = math.sqrt(105 ** 2 + 105 ** 2)

	# time check is two seconds
	duration = 1.0

	# Setup three global variables, x, y and timestamp.
	# So we can compare different between
	# those messages
	x = -1.0
	y = -1.0
	timestamp = -1

	# set up the global value for printing message
	cmd_out = 'input tap {} {}'
	# dictionary key
	key = 'realtime gaze on nexus'

	# set up network connection with pupil eye tracker
	port = '5000'
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect('tcp://127.0.0.1:' + port)
	# filter by message by stating string "STRING". '' receives all messages
	socket.setsockopt(zmq.SUBSCRIBE, '')


	# # build up an adb object
	# adb = ADB()
	# set ADB path
	adb.set_adb_path('~/Library/Android/sdk/platform-tools/adb')

	# verify ADB path
	print "[+] Verifying ADB path ..."
	if adb.check_path() is False:
		print "Error"
		exit(-1)
	print "OK"

	# restart server ???
	print "[+] Restarting ADB server"
	adb.restart_server()
	if adb.lastFailed():
		print "\t- Error\n"
		adb.kill_server()
		exit(-2)

	# get detected devices
	dev = 0
	while dev is 0:
		print "[+] Detecting devices..."
		error, devices = adb.get_devices()

		if error is 1:
			# no devices connected
			adb.wait_for_device()
			continue
		elif error is 2:
			print "Not enough permissions !"
			adb.kill_server()
			exit(-3)

		print "OK"
		dev = 1

	# this should never reached
	if len(devices) == 0:
		print "[+] No devices detected !"
		exit(-4)

	# show detected devices
	i = 0
	for dev in devices:
		print "\t%d: %s" % (i, dev)
		i += 1

	if i > 1:
		print 'more than 1 devices'
		exit(0)
	else:
		dev = 0

	# set target device
	try:
		adb.set_target_device(devices[dev])
	except Exception, e:
		print "\n[!] Error:\t- ADB: %s\t - Python: %s" % (adb.get_error(),e.args)
		adb.kill_server()
		exit(-5)

	print "[+] Using \"%s\" as target device " % (devices[dev])
	# connect device with client by TCP/IP
	# set listening port
	adbPort = input("Enter an port number except for 5000: ")
	if adbPort == 5000:
		adb.kill_server()
		print "Port error"
		exit(-1)
	# listen to the port
	adb.listen_tcp(adbPort)
	# set the ip address for listening
	ip_addr = input("Enter device ip address: ")
	adb.connect_remote(ip_addr, adbPort)

	print "[+] Using \"%s\" as target device " % (devices[dev])

	rain = input("Please disconnect usb : ")
 	if rain in ("No" or "N" or "Nope"):
 		adb.kill_server()
 		exit(0)

 	print "Check"

	# accepting connection from pupil head set
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

						# debugging aid
						print 'x: {}, y: {}, timestamp: {}'.format(x, y, timestamp)
						print 'temp_x: {}, temp_y: {}, temp_timestamp: {}'.format(temp_x, temp_y, temp_timestamp)
						# debugging aid
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
									result =  cmd_out.format(x, y)
									# debugging aid
									print result
									adb.shell_command(result)
									x = -1.0
									y = -1.0
									timestamp = -1.0
							else:
								# case: new gaze locataion is outside range
								# replace the standard point to new gaze_location
								x = temp_x
								y = temp_y
								timestamp = temp_timestamp
				else:
					# case: confidence less than lowest confident level
					pass
			except KeyError:
				print error_message
				break
		else:
			# pass on other messages not related to gaze position
			pass

if __name__ == "__main__":
	main()
	signal.signal(signal.SIGINT, signal_handler)
