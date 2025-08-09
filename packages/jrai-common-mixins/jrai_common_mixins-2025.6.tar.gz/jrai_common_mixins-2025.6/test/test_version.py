#!/usr/bin/env python3
"""
Test version.py.
"""

import unittest

import jrai_common_mixins.version as ver


class TestVersion(unittest.TestCase):
    """
    Test the automatically generated version.py file.
    """

    def test_version(self):
        """
        VERSION is a string.
        """
        self.assertIsInstance(ver.VERSION, str)

    def test_version_tuple(self):
        """
        VERSION_TUPLE is a tuple.
        """
        self.assertIsInstance(ver.VERSION_TUPLE, tuple)


if __name__ == "__main__":
    unittest.main()
