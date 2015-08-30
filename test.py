#!/usr/bin/python2.7
import matplotlib.pyplot as plt
import numpy as np
gaze_positions = np.load("/Users/zzt124/Pupil_Lab/pupil/recordings/2015_08_27/000/pupil_positions.npy")
X = gaze_positions[:,2]
Y = gaze_positions[:,3]
plt.scatter(X,Y)
plt.show()