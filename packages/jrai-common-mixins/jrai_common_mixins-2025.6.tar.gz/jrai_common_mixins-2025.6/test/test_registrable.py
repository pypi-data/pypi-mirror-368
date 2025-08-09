#!/usr/bin/env python3
"""
Test registrable.py.
"""

import unittest

from jrai_common_mixins.registrable import Registrable


class BaseClass(Registrable):  # pylint: disable=too-few-public-methods
    """
    Subclass of Registrable that serves as a base class for registrable classes.
    """


class FirstBaseClass(BaseClass):  # pylint: disable=too-few-public-methods
    """
    First registrable class for testing. This is registered during setup.
    """


class SecondBaseClass(BaseClass):  # pylint: disable=too-few-public-methods
    """
    Second registrable class for testing. This is not registered during setup.
    """


class Third(BaseClass):  # pylint: disable=too-few-public-methods
    """
    Class that doesn't following naming convention.
    """


class TestRegistrable(unittest.TestCase):
    """
    Test Registrable.
    """

    def setUp(self):
        BaseClass.clear_registered()
        FirstBaseClass.register()

    def test_get_registration_base_class(self):
        """
        Registrable subclasses return their base class.
        """
        for subcls in (FirstBaseClass, SecondBaseClass):
            with self.subTest(subclass=subcls):
                self.assertEqual(subcls.get_registration_base_class(), BaseClass)

    def test_get_registration_name(self):
        """
        Registrable subclass return their name.
        """
        for expected_name, subcls in (
            ("First", FirstBaseClass),
            ("Second", SecondBaseClass),
            ("Third", Third),
        ):
            with self.subTest(subclass=subcls, expected_name=expected_name):
                self.assertEqual(subcls.get_registration_name(), expected_name)

    def test_clear_registered(self):
        """
        Registered subclasses are cleared on request.
        """
        self.assertEqual(BaseClass.list_registered(), ["First"])
        BaseClass.clear_registered()
        self.assertEqual(BaseClass.list_registered(), [])

    def test_registration(self):
        """
        Registrable subclasses are registered.
        """
        self.assertEqual(BaseClass.list_registered(), ["First"])
        SecondBaseClass.register()
        self.assertEqual(BaseClass.list_registered(), ["First", "Second"])
        Third.register(name="xyz")
        self.assertEqual(BaseClass.list_registered(), ["First", "Second", "xyz"])

    def test_invalid_registration_name(self):
        """
        Invalid registration names raise ValueErrors.
        """
        for name in ("", 5, False):
            with self.subTest(name=name), self.assertRaises(ValueError):
                Third.register(name=name)

    def test_get_registered(self):
        """
        Registrable subclasses are returned on request.
        """
        self.assertEqual(BaseClass.get_registered("First"), FirstBaseClass)
        SecondBaseClass.register()
        self.assertEqual(BaseClass.get_registered("Second"), SecondBaseClass)

    def test_get_unregistered(self):
        """
        Requesting unregistered subclasses raises a ValueError.
        """
        with self.assertRaises(ValueError):
            BaseClass.get_registered("Second")


if __name__ == "__main__":
    unittest.main()
