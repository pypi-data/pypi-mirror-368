# test_runner.py

import unittest


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    runner = unittest.TextTestRunner()
    runner.run(suite)
