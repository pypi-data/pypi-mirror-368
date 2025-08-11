from time import sleep
import unittest
from time import sleep
from pybeans import utils

class CoreTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    @utils.benchmark
    def testBenchmark(self):
        sleep(3.5)
        
    def testFormatDuration(self):
        self.assertEqual(utils.format_duration(0.345), '345ms')
        self.assertEqual(utils.format_duration(0.3456), '345.6ms')
        self.assertEqual(utils.format_duration(12.3456), '12.346s')
        self.assertEqual(utils.format_duration(123.4567), '2m 3.457s')
        self.assertEqual(utils.format_duration(123.45), '2m 3.45s')
        self.assertEqual(utils.format_duration(123), '2m 3s')
        self.assertEqual(utils.format_duration(3600 + 123.4567), '1h 2m 3.457s')
        self.assertEqual(utils.format_duration(25 * 3600 + 123.4567), '1d 1h 2m 3.457s')
        self.assertEqual(utils.format_duration(7 * 24 * 3600 + 3600 + 123.4567), '1w 1h 2m 3.457s')
        self.assertEqual(utils.format_duration(8 * 24 * 3600 + 3600 + 123.4567), '1w 1d 1h 2m 3.457s')
        
        
    def testFormatSize(self):
        self.assertEqual(utils.format_size(123), '123B')
        self.assertEqual(utils.format_size(1024 + 123), '1.12KB')
        self.assertEqual(utils.format_size(1024), '1KB')
        self.assertEqual(utils.format_size(1024 * 1024 + 30 * 1024), '1.03MB')
        self.assertEqual(utils.format_size(1024 * 1024 * 1024 + 24 * 1024 * 1024 + 30 * 1024), '1.02GB')
        self.assertEqual(utils.format_size(1024 * 1024 * 1024 * 1024 + 24 * 1024 * 1024 * 1024), '1.02TB')