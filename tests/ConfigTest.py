import unittest
from MLC.Config.Config import Config
import os
import numpy as np

class ConfigTest(unittest.TestCase):
    def setUp(self):
        self._file = open('test', 'w+')
        self._file.write('[TEST]\n')
        self._file.write('arange = 1:10\n')
        self._file.write('arange_step = 1:13:3\n')
        self._file.write('array = 1,2,3,4\n')
        self._file.close()
        self._config = Config()
        self._config.read('test')

    def tearDown(self):
        os.remove('test')
        self._config = None

    def test_array_creation(self):
        expected = np.array([1, 2, 3, 4])
        actual = self._config.get_param('TEST', 'array', type='array')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)

    def test_arange_creation_without_step(self):
        expected = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual = self._config.get_param('TEST', 'arange', type='arange')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)

    def test_arange_creation_with_step(self):
        expected = np.array([1, 4, 7, 10])
        actual = self._config.get_param('TEST', 'arange_step', type='arange')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)



def suite():
    a_suite = unittest.TestSuite()
    a_suite.addTest(ConfigTest())
    return a_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
