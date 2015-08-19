import matplotlib.pyplot as plt
import numpy as np
'''
	Use calibration points cloud to calculate
	the minimum, maximum, standard deviation of
	points in each cluster. There are total 10
	markers for calibraiton.
'''
# load cal_pt_cloud
cal_pt_cloud = np.load("/Users/zzt124/Desktop/003/cal_pt_cloud.npy")
# reminder : the format of the cal_pt_cloud
# is 'norm_pupil_x', 'norm_pupil_y', 'target_x' and 'target_y'
storage = {'1': None,
			'2': None,
			'3': None,
			'4': None,
			'5': None,
			'6': None,
			'7': None,
			'8': None,
			'9': None,
			'10': None}
# norm_pupil_x = cal_pt_cloud[:,0]
# norm_pupil_y = cal_pt_cloud[:,1]

# group those pupil center into ten different clusters
end_index = 0
start_index = 0
count = 1;
# starting point
start_point = None
for val in cal_pt_cloud:
	val = np.around(val, decimals = 5)
	if start_point == None:
		# case 1: start_point is none
		start_point = val[2:4].tolist()
	else:
		# case 2: start_point isn't none
		# calculate the difference between x and y
		x_diff = abs(val[2] - start_point[0])
		y_diff = abs(val[3] - start_point[1])
		if x_diff > 0.06 or y_diff > 0.06:
			# by observation, the minimum between each marker point
			# is 0.6.
			# case: reach a new cluster for marker
			cluster = cal_pt_cloud[start_index:end_index, 0:2]
			storage[str(count)] = cluster
			count += 1
			start_index = end_index
			start_point = val[2:4].tolist()
	# increase the last element index
	end_index += 1
# storage the very last point
storage['10'] = cal_pt_cloud[start_index:, 0:2]

# Next step: calculate min, max, avg, standard diviation of X,Y
for key, val in storage.items():
	print "Current key is %s" % (key)
	min_x = np.amin(val[:,0])
	min_y = np.amin(val[:,1])
	max_x = np.amax(val[:,0])
	max_y = np.amax(val[:,1])
	avg_x = np.mean(val[:,0])
	avg_y = np.mean(val[:,1])
	med_x = np.median(val[:,0])
	med_y = np.median(val[:,1])
	std_x = np.std(val[:,0])
	std_y = np.std(val[:,1])
	print "min_x = %.4f, min_y = %.4f, max_x = %.4f, max_y = %.4f, avg_x = %.4f, avg_y = %.4f" % (min_x, min_y, max_x, max_y, avg_x, avg_y)
	print "med_x = %.4f, med_y = %.4f, std_x = %.4f, std_y = %.4f" % (med_x, med_y, std_x, std_y)

