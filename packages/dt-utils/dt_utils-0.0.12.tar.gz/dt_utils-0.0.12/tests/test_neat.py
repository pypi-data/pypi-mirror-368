import unittest
from dt_utils.parsers import *
from dt_utils.neat import *


class TestNeat(unittest.TestCase):
    def test_latest_neat(self):
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='T'), T(202405010947))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='10T'), T(202405010940))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='15T'), T(202405010945))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='1h'), T(2024050109))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='1D'), T(20240501))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='M'), T(20240501))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='1M'), T(20240501))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='3M'), T(20240401))
        self.assertEqual(get_latest_neat_time(T(202405010947), freq='Y'), T(20240101))
        self.assertEqual(get_latest_neat_time(T(202305010947), freq='4Y'), T(20200101))

    def test_nearest_neat(self):
        self.assertEqual(get_nearest_neat_time(T(202405010947), freq='15T'), T(202405010945))
        self.assertEqual(get_nearest_neat_time(T(202405010947), freq='10T'), T(202405010950))
        self.assertEqual(get_nearest_neat_time(T(202405010947), freq='1M'), T(20240501))
        self.assertEqual(get_nearest_neat_time(T(202405210947), freq='1M'), T(20240601))
        self.assertEqual(get_nearest_neat_time(T(202105210947), freq='4Y'), T(20200101))
        self.assertEqual(get_nearest_neat_time(T(202305210947), freq='4Y'), T(20240101))

    def test_neat_beg_end(self):
        # TODO: test
        pass


if __name__ == '__main__':
    unittest.main()
