# -*- coding:utf-8 -*-

import six
import unittest
from hypothesis import given
import hypothesis.strategies as st
import hypothesis.extra.numpy as np_st

import numpy as np
from dt_utils.parsers import *


class TestParseTDelta(unittest.TestCase):
    def test_legacy_plain_format(self):
        self.assertEqual(TD('15m'), timedelta(minutes=15))
        self.assertEqual(TD('1d'), timedelta(days=1))
        self.assertEqual(TD('2h'), timedelta(hours=2))
        self.assertEqual(TD('30s'), timedelta(seconds=30))
        self.assertEqual(TD('60'), timedelta(seconds=60))

    def test_legacy_relative_format(self):
        self.assertEqual(TD('2M'), relativedelta(months=2))
        self.assertEqual(TD('1Y'), relativedelta(years=1))
        self.assertEqual(TD('7W'), relativedelta(weeks=7))

    def test_pd_compatible_format(self):
        self.assertEqual(TD('15T'), timedelta(minutes=15))
        self.assertEqual(TD('15min'), timedelta(minutes=15))
        self.assertEqual(TD('1D'), timedelta(days=1))
        self.assertEqual(TD('2H'), timedelta(hours=2))
        self.assertEqual(TD('30S'), timedelta(seconds=30))

    def test_without_number(self):
        self.assertEqual(TD('T'), timedelta(minutes=1))
        self.assertEqual(TD('min'), timedelta(minutes=1))
        self.assertEqual(TD('D'), timedelta(days=1))
        self.assertEqual(TD('H'), timedelta(hours=1))
        self.assertEqual(TD('S'), timedelta(seconds=1))
        self.assertEqual(TD('m'), timedelta(minutes=1))
        self.assertEqual(TD('d'), timedelta(days=1))
        self.assertEqual(TD('h'), timedelta(hours=1))
        self.assertEqual(TD('s'), timedelta(seconds=1))
        self.assertEqual(TD(''), timedelta(seconds=1))

    def test_number(self):
        self.assertEqual(TD(3600), timedelta(hours=1))

    def test_hh_mm_ss(self):
        self.assertEqual(TD('1:20:35'), timedelta(hours=1) + timedelta(minutes=20) + timedelta(seconds=35))
        self.assertEqual(TD('1:20'), timedelta(minutes=1) + timedelta(seconds=20))

    def test_invalid(self):
        self.assertIsNone(TD('1what'))
        self.assertIsNone(TD('ablaksjedoij1i2jalskjdf'))
        self.assertIsNone(TD(None))

    def test_list(self):
        self.assertListEqual(TD([
            '15m', '1H', 3600, None
        ]), [
            timedelta(minutes=15), timedelta(hours=1), timedelta(seconds=3600), None
        ])

    def test_array(self):
        result = TD(np.array([
            '15m', '1H', 3600, None
        ]))
        self.assertIsInstance(result, np.ndarray)
        self.assertListEqual(list(result), [
            timedelta(minutes=15), timedelta(hours=1), timedelta(seconds=3600), None
        ])


if __name__ == '__main__':
    unittest.main()