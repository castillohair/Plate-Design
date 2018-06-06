# -*- coding: UTF-8 -*-
"""
Unit tests for math functions
"""

import unittest
import numpy

import platedesign
import platedesign.math

class TestCeilLog(unittest.TestCase):
    """
    Class to test the ceil_log function

    """
    def test_input_1_r1(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(932), 1000.)

    def test_input_1_r2(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(932, 2), 940.)

    def test_input_1_r3(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(932, 3), 932.)

    def test_input_2_r1(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(70), 70.)

    def test_input_2_r2(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(70), 70.)

    def test_input_3_r1(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(71), 80.)

    def test_input_3_r2(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(71, 2), 71.)

    def test_input_4_r1(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(69.1), 70.)

    def test_input_4_r2(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(69.1, 2), 70.)

    def test_input_5(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(6.91), 7.)

    def test_input_6(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(9.9), 10.)

    def test_array_1(self):
        """
        Test for correct processing of an input array.

        """
        x = numpy.array([34, 67, 5.61])
        y = platedesign.math._ceil_log(x)
        y_exp = numpy.array([ 40., 70., 6.])
        numpy.testing.assert_array_equal(y, y_exp)

    def test_array_1_r2(self):
        """
        Test for correct processing of an input array.

        """
        x = numpy.array([34, 67, 5.61])
        y = platedesign.math._ceil_log(x, 2)
        y_exp = numpy.array([ 34., 67., 5.7])
        numpy.testing.assert_array_equal(y, y_exp)

    def test_array_1_r_array(self):
        """
        Test for correct processing of an input array.

        """
        x = numpy.array([34, 67, 5.61])
        r = numpy.array([1, 2, 2])
        y = platedesign.math._ceil_log(x, r)
        y_exp = numpy.array([ 40., 67., 5.7])
        numpy.testing.assert_array_equal(y, y_exp)
