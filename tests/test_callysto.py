#!/usr/bin/env python
import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import callysto


class TestCallysto(unittest.TestCase):
    def test_evaluate(self):
        with open("tests/fixtures/example.callysto") as fh:
            callysto.evaluate(fh)

    def test_generate(self):
        with open("tests/fixtures/example.callysto") as fh:
            callysto.generate(fh)


if __name__ == '__main__':
    unittest.main()
