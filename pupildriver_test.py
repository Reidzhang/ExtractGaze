#!/usr/bin/python
import unittest
import identify_pupildirection
import pdb

class TestDetAngle(unittest.TestCase):
	'''
		Test calculation of convertion between normalized
		space and angels.
		This is white-box testing.
	'''
	def test_first_quadrant(self):
		# check for calculation of first quadrant
		# first point
		# pdb.set_trace()
		val = identify_pupildirection.det_angle(0.85, '(0.7, 0.6)', 0.65)
		self.assertTrue(val >= 270)
		self.assertTrue(val < 360)
		# second point
		val1 = identify_pupildirection.det_angle(0.85, '(0.75, 0.5)', 0.65)
		self.assertTrue(val1 >= 270)
		self.assertTrue(val1 < 360)

	def test_second_quadrant(self):
		# check for calculation of second quadrant
		# first data point
		val = identify_pupildirection.det_angle(0.85, '(0.3, 0.65)', 0.65)
		self.assertTrue(val >= 0)
		self.assertTrue(val <= 90)
		# second data point
		val1 = identify_pupildirection.det_angle(0.85, '(0.45, 0.9)', 0.65)
		self.assertTrue(val1 >= 0)
		self.assertTrue(val1 <= 90)

	def test_third_quadrant(self):
		# check for calculation of third quadrant
		val = identify_pupildirection.det_angle(0.85, '(0.4, 0.4)', 0.65)
		self.assertTrue(val > 90)
		self.assertTrue(val <= 180)
		val1 = identify_pupildirection.det_angle(0.85, '(0.1, 0.1)', 0.65)
		self.assertTrue(val1 > 90)
		self.assertTrue(val1 <= 180)

	def test_fourth_quadrant(self):
		# check for calculation of fourth quadrant
		val = identify_pupildirection.det_angle(0.85, '(0.7, 0.49)', 0.65)
		self.assertTrue(val > 180)
		self.assertTrue(val < 270)
		val1 = identify_pupildirection.det_angle(0.85, '(0.56, 0.1)', 0.65)
		self.assertTrue(val1 > 180)
		self.assertTrue(val1 < 270)

	def test_nonangel(self):
		# check for within consider threshold
		self.assertEqual(identify_pupildirection.det_angle(1, '(0.5, 0.5)', 0.65), None)
		self.assertEqual(identify_pupildirection.det_angle(0.80, '(0.5, 0.55)', 0.65), None)

	def test_less_confident(self):
		# check for less confident
		self.assertEqual(identify_pupildirection.det_angle(0.50, '(0.60, 0.70)', 0.65), None)
		self.assertEqual(identify_pupildirection.det_angle(0.60, '(0.4, 0.4)', 0.65), None)


