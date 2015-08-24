'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2015  Pupil Labs
 Distributed under the terms of the CC BY-NC-SA License.
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''
def fit_poly_surface(cal_pt_cloud,n=7):
    M = make_model(cal_pt_cloud,n)
    U,w,Vt = np.linalg.svd(M[:,:n],full_matrices=0)
    V = Vt.transpose()
    Ut = U.transpose()
    pseudINV = np.dot(V, np.dot(np.diag(1/w), Ut))
    cx = np.dot(pseudINV, M[:,n])
    cy = np.dot(pseudINV, M[:,n+1])
    # compute model error in world screen units if screen_res specified
    err_x=(np.dot(M[:,:n],cx)-M[:,n])
    err_y=(np.dot(M[:,:n],cy)-M[:,n+1])
    return cx,cy,err_x,err_y

def fit_error_screen(err_x,err_y,(screen_x,screen_y)):
    err_x *= screen_x/2.
    err_y *= screen_y/2.
    err_dist=np.sqrt(err_x*err_x + err_y*err_y)
    err_mean=np.sum(err_dist)/len(err_dist)
    err_rms=np.sqrt(np.sum(err_dist*err_dist)/len(err_dist))
    return err_dist,err_mean,err_rms

def make_model(cal_pt_cloud,n=7):
    n_points = cal_pt_cloud.shape[0]

    if n==3:
        X=cal_pt_cloud[:,0]
        Y=cal_pt_cloud[:,1]
        Ones=np.ones(n_points)
        ZX=cal_pt_cloud[:,2]
        ZY=cal_pt_cloud[:,3]
        M=np.array([X,Y,Ones,ZX,ZY]).transpose()

    elif n==7:
        X=cal_pt_cloud[:,0]
        Y=cal_pt_cloud[:,1]
        XX=X*X
        YY=Y*Y
        XY=X*Y
        XXYY=XX*YY
        Ones=np.ones(n_points)
        ZX=cal_pt_cloud[:,2]
        ZY=cal_pt_cloud[:,3]
        M=np.array([X,Y,XX,YY,XY,XXYY,Ones,ZX,ZY]).transpose()

    elif n==9:
        X=cal_pt_cloud[:,0]
        Y=cal_pt_cloud[:,1]
        XX=X*X
        YY=Y*Y
        XY=X*Y
        XXYY=XX*YY
        XXY=XX*Y
        YYX=YY*X
        Ones=np.ones(n_points)
        ZX=cal_pt_cloud[:,2]
        ZY=cal_pt_cloud[:,3]
        M=np.array([X,Y,XX,YY,XY,XXYY,XXY,YYX,Ones,ZX,ZY]).transpose()
    else:
        raise Exception("ERROR: Model n needs to be 3, 7 or 9")
    return M


def make_map_function(cx,cy,n):
    if n==3:
        def fn((X,Y)):
            x2 = cx[0]*X + cx[1]*Y +cx[2]
            y2 = cy[0]*X + cy[1]*Y +cy[2]
            return x2,y2

    elif n==7:
        def fn((X,Y)):
            x2 = cx[0]*X + cx[1]*Y + cx[2]*X*X + cx[3]*Y*Y + cx[4]*X*Y + cx[5]*Y*Y*X*X +cx[6]
            y2 = cy[0]*X + cy[1]*Y + cy[2]*X*X + cy[3]*Y*Y + cy[4]*X*Y + cy[5]*Y*Y*X*X +cy[6]
            return x2,y2

    elif n==9:
        def fn((X,Y)):
            #          X         Y         XX         YY         XY         XXYY         XXY         YYX         Ones
            x2 = cx[0]*X + cx[1]*Y + cx[2]*X*X + cx[3]*Y*Y + cx[4]*X*Y + cx[5]*Y*Y*X*X + cx[6]*Y*X*X + cx[7]*Y*Y*X + cx[8]
            y2 = cy[0]*X + cy[1]*Y + cy[2]*X*X + cy[3]*Y*Y + cy[4]*X*Y + cy[5]*Y*Y*X*X + cy[6]*Y*X*X + cy[7]*Y*Y*X + cy[8]
            return x2,y2
    else:
        raise Exception("ERROR: Model n needs to be 3, 7 or 9")

    return fn


if __name__ == '__main__':
	import matplotlib.pyplot as plt
	from matplotlib import cm
	from mpl_toolkits.mplot3d import Axes3D
	import numpy as np
	'''
	Use calibration points cloud to calculate
	the minimum, maximum, standard deviation of
	points in each cluster. There are total 10
	markers for calibraiton.
	'''
	cal_pt_cloud = np.load('/Users/zzt124/Pupil_Lab/pupil/recordings/2015_08_21/004/cal_pt_cloud.npy')
	# reminder : the format of the cal_pt_cloud
	# is 'norm_pupil_x', 'norm_pupil_y', 'target_x' and 'target_y'
	storage = {1: None,
			2: None,
			3: None,
			4: None,
			5: None,
			6: None,
			7: None,
			8: None,
			9: None,
			10: None}
	# norm_pupil_x = cal_pt_cloud[:,0]
	# norm_pupil_y = cal_pt_cloud[:,1]


	# model_n = 9
	# cx,cy,err_x,err_y = fit_poly_surface(cal_pt_cloud,model_n)
	# map_fn = make_map_function(cx,cy,model_n)
	# X,Y,ZX,ZY = cal_pt_cloud.transpose().copy()
	# X,Y = map_fn((X,Y))
	# cal_pt_cloud_mapped = np.dstack((X,Y))
	# cal_pt_cloud_mapped = np.dstack((cal_pt_cloud_mapped, ZX))
	# cal_pt_cloud_mapped = np.dstack((cal_pt_cloud_mapped, ZY))
	# cal_pt_cloud_mapped = cal_pt_cloud_mapped[0]
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
				# cluster = cal_pt_cloud[start_index:end_index, 0:2]
				storage[count] = start_index, end_index
				count += 1
				start_index = end_index
				start_point = val[2:4].tolist()
		# increase the last element index
		end_index += 1
	# storage the very last point
	# storage['10'] = cal_pt_cloud[start_index:, 0:2]
	storage[10] = start_index, end_index
	model_n = 9
	cx,cy,err_x,err_y = fit_poly_surface(cal_pt_cloud, model_n)
	X,Y,ZX,ZY = cal_pt_cloud.transpose().copy()
	for key in sorted(storage):
		val = storage[key]
		tmp_dist, tmp_mean, tmp_rms = fit_error_screen(err_x[val[0]:val[1]], err_y[val[0]:val[1]], (1920, 1080))
		M_X = ZX[val[0]] * 1920
		M_Y = ZY[val[0]] * 1080
		print 'Marker (%0.4f, %0.4f) has err_rms = %0.4f in pixel' % (M_X, M_Y, tmp_rms)

	map_fn = make_map_function(cx,cy,model_n)
	err_dist, err_mean, err_rms = fit_error_screen(err_x, err_y, (1920, 1080))
	threshold = err_rms * 2
	cx,cy,new_err_x,new_err_y = fit_poly_surface(cal_pt_cloud[err_dist<=threshold], model_n)
	map_fn = make_map_function(cx,cy,model_n)
	new_err_dist, new_err_mean, new_err_rms = fit_error_screen(new_err_x, new_err_y, (1920,1080))
	X,Y = map_fn((X,Y))
	X *= 1920.
	Y *= 1080.
	ZX *= 1920.
	ZY *= 1080.
	fig_projection = plt.figure()
	plt.scatter(X,Y)
	plt.scatter(ZX,ZY,c='y')
	plt.title("world space projection in pixes, mapped and observed (y)")
	plt.show()
	
