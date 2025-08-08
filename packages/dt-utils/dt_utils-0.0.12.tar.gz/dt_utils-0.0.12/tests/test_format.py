import unittest
from dt_utils.parsers import T
from dt_utils.format import *

import numpy as np


class TestFormat(unittest.TestCase):
    def test_minimal_timestr(self):
        self.assertEqual(minimal_timestr(T(202305010000)), '20230501')
        self.assertEqual(minimal_timestr(T(202305010800)), '2023050108')
        self.assertEqual(minimal_timestr(T(20240601231500)), '202406012315')
        self.assertEqual(minimal_timestr(T(20240601231523)), '20240601231523')
        self.assertEqual(minimal_timestr('202301031200'), '2023010312')
        self.assertEqual(minimal_timestr(None), None)

        self.assertListEqual(minimal_timestr(['202301', '2023021500']), ['20230101', '20230215'])
        arr_result = minimal_timestr(np.array(['202301', '2023021500']))
        self.assertIsInstance(arr_result, np.ndarray)
        self.assertListEqual(list(arr_result), ['20230101', '20230215'])

    def test_simple_timestr(self):
        self.assertEqual(simple_timestr(202305010000, freq='1Y', minimal=False), '2023')
        self.assertEqual(simple_timestr(202305010000, freq='1M', minimal=False), '2023-05')
        self.assertEqual(simple_timestr(202305010000, freq='1H', minimal=False), '2023-05-01 00')
        self.assertEqual(simple_timestr(202305010000, freq='15m', minimal=False), '2023-05-01 00:00')
        self.assertListEqual(simple_timestr([20230501, 20230502], freq='1D', minimal=False), ['2023-05-01', '2023-05-02'])

    def test_simple_timestr_minimal(self):
        self.assertEqual(simple_timestr(202305010000, freq='1Y'), '2023')
        self.assertEqual(simple_timestr(202305010000, freq='1M'), '202305')
        self.assertEqual(simple_timestr(202305010000, freq='1H'), '2023050100')
        self.assertEqual(simple_timestr(202305010000, freq='15m'), '202305010000')
        self.assertListEqual(simple_timestr([20230501, 20230502], freq='1D'), ['20230501', '20230502'])


if __name__ == '__main__':
    unittest.main()
