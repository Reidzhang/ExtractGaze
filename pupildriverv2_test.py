#!/usr/bin/python
import unittest
import pupil_driver_v2
import pdb

class TestDetAngle(unittest.TestCase):
	'''
		Test calculation angel difference
		between two points
	'''
	def test_first_quadrant(self):
		# check the end point is at the
		# first quadrant of start point
		start_point = [0.2,0.3]
		end_point = [0.5,0.5]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res >= 0)
		self.assertTrue(res <= 90)
		start_point = [0.3, 0.4]
		end_point = [0.5, 0.6]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res >= 0)
		self.assertTrue(res <= 90)

	def test_second_quadrant(self):
		# check the end point is at the
		# second quadrant of start point
		start_point = [0.4, 0.6]
		end_point = [0.6, 0.4]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 90)
		self.assertTrue(res <= 180)
		start_point = [0.4, 0.6]
		end_point = [0.4, 0.5]
		# pdb.set_trace()
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 90)
		self.assertTrue(res <= 180)

	def test_third_quadrant(self):
		# check the end point at the
		# third quadrant of start point
		start_point = [0.4, 0.6]
		end_point = [0.2, 0.1]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 180)
		self.assertTrue(res <= 270)
		start_point = [0.4, 0.3]
		end_point = [0.1, 0.3]
		# pdb.set_trace()
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 180)
		self.assertTrue(res <= 270)

	def test_fouth_quadrant(self):
		start_point = [0.6, 0.1]
		end_point = [0.3, 0.4]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 270)
		self.assertTrue(res <= 359)
		# second data point
		start_point = [0.1, 0.6]
		end_point = [0, 0.86]
		res = pupil_driver_v2.det_angle(start_point, end_point)
		self.assertTrue(res > 270)
		self.assertTrue(res <= 359)


