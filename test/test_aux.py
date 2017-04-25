"""
Unit tests for auxiliary functions
"""

import unittest
import numpy

import platedesign
import platedesign.math

class TestCeilLog(unittest.TestCase):
    """
    Class to test the ceil_log function

    """
    def test_input_1(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(932), 1000.)

    def test_input_2(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(70), 70.)

    def test_input_3(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(71), 80.)

    def test_input_4(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(69), 70.)

    def test_input_5(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(6.9), 7.)

    def test_input_6(self):
        """
        Test for correct processing of an input.

        """
        self.assertAlmostEqual(platedesign.math._ceil_log(9.9), 10.)

    def test_array_1(self):
        """
        Test for correct processing of an input array.

        """
        x = numpy.array([34, 67, 5.6])
        y = platedesign.math._ceil_log(x)
        y_exp = numpy.array([ 40., 70., 6.])
        numpy.testing.assert_array_equal(y, y_exp)
