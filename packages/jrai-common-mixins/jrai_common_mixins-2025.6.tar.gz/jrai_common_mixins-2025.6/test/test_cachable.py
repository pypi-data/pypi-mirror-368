#!/usr/bin/env python3
"""
Test cachable.py.
"""

import datetime
import inspect
import time
import unittest

from freezegun import freeze_time

from jrai_common_mixins.cachable import Cachable


def _closer_than_three(arg1, arg2):
    return abs(arg1 - arg2) < 3


def _begins_with_same_letter(arg1, arg2):
    arg1 = str(arg1)
    arg2 = str(arg2)
    return arg1 and arg2 and arg1[0] == arg2[0]


class MyCachable(Cachable):
    """
    Subclass for testing cachable.
    """

    def __init__(self):
        super().__init__()
        self.calls = {}

    def _increment(self):
        # Get name of calling function.
        name = inspect.stack()[1][3]
        value = self.calls.setdefault(name, 0) + 1
        self.calls[name] = value
        return value

    @property
    def uncached_prop(self):
        """
        Uncached property.
        """
        return self._increment()

    @Cachable.caching_property
    def cached_prop(self):
        """
        Cached property.
        """
        return self._increment()

    def uncached_meth(self, arg1, arg2, kwarg1=None):
        """
        Uncached method.
        """
        return f"uncached_meth,{arg1},{arg2},{kwarg1},{self._increment()}"

    @Cachable.caching_method()
    def cached_meth(self, arg1, arg2, kwarg1=None):
        """
        Cached method.
        """
        return f"cached_meth,{arg1},{arg2},{kwarg1},{self._increment()}"

    @Cachable.caching_method(None, _closer_than_three, kwarg1=_begins_with_same_letter)
    def cached_meth_with_custom_cmps(self, arg1, arg2, kwarg1=None):
        """
        Cached method.
        """
        return f"cached_meth,{arg1},{arg2},{kwarg1},{self._increment()}"

    @Cachable.caching_method(_cm_maxsize=3)
    def cached_meth_with_maxsize(self, arg1):
        """
        Cached method with max cache size.
        """
        return f"cached_meth,{arg1},{self._increment()}"


class TestCachable(unittest.TestCase):
    """
    Test Cachable.
    """

    def setUp(self):
        self.myc = MyCachable()

    def test_uncached_prop(self):
        """
        Regular properties are not cached.
        """
        self.assertEqual(self.myc.uncached_prop, 1)
        self.assertEqual(self.myc.uncached_prop, 2)

    def test_cached_prop(self):
        """
        Cached properties return cached values.
        """
        self.assertEqual(self.myc.cached_prop, 1)
        self.assertEqual(self.myc.cached_prop, 1)

    def test_clear_cached_property(self):
        """
        Cached properties are cleared on request.
        """
        self.assertEqual(self.myc.cached_prop, 1)
        self.myc.clear_cached_property("cached_prop")
        self.assertEqual(self.myc.cached_prop, 2)

    def test_uncached_meth(self):
        """
        Regular methods are not cached.
        """
        self.assertEqual(
            self.myc.uncached_meth(1, 2, kwarg1=3), "uncached_meth,1,2,3,1"
        )
        self.assertEqual(
            self.myc.uncached_meth(1, 2, kwarg1=3), "uncached_meth,1,2,3,2"
        )

    def test_cached_meth(self):
        """
        Cached methods return cached values.
        """
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")
        self.assertEqual(self.myc.cached_meth(1, "a", kwarg1=3), "cached_meth,1,a,3,2")
        self.assertEqual(self.myc.cached_meth(1, "a", kwarg1=3), "cached_meth,1,a,3,2")

    def test_cached_meth_with_custom_cmp(self):
        """
        Cached methods use custom argument comparison functions.
        """
        expected = "cached_meth,1,2,foo,1"
        self.assertEqual(
            self.myc.cached_meth_with_custom_cmps(1, 2, kwarg1="foo"), expected
        )
        self.assertEqual(
            self.myc.cached_meth_with_custom_cmps(1, 4, kwarg1="foo"), expected
        )
        self.assertEqual(
            self.myc.cached_meth_with_custom_cmps(1, 2, kwarg1="fifi"), expected
        )

    def test_cached_meth_with_mixed_positional_and_keyword_args(self):
        """
        Mixed positional and keyword arguments are recognized.
        """
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")
        self.assertEqual(self.myc.cached_meth(1, 2, 3), "cached_meth,1,2,3,1")
        self.assertEqual(self.myc.cached_meth(1, 2, 4), "cached_meth,1,2,4,2")
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=4), "cached_meth,1,2,4,2")

    def test_duplicate_argument_detection(self):
        """
        Duplicate arguments raise errors.
        """
        with self.assertRaises(TypeError):
            # Pass third argument by position and keyword.
            # pylint: disable=redundant-keyword-arg
            self.myc.cached_meth(1, 2, 3, kwarg1=4)

    def test_clear_cached_method(self):
        """
        Cached methods are cleared on request.
        """
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")
        self.myc.clear_cached_method("cached_meth")
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2")
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2")
        self.myc.clear_cached_method(self.myc.cached_meth)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,3")

    def test_clear_cache(self):
        """
        The full cache is cleared on request.
        """
        self.assertEqual(self.myc.cached_prop, 1)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")
        self.myc.clear_cache()
        self.assertEqual(self.myc.cached_prop, 2)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2")

    def test_clear_old_cache_entries(self):
        """
        Old cache entries are cleared by age.
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        for by_atime in (True, False):
            self.myc.calls.clear()
            self.myc.clear_cache()
            with self.subTest(by_atime=by_atime):
                with freeze_time(yesterday):
                    self.assertEqual(self.myc.cached_prop, 1)
                    self.assertEqual(
                        self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
                    )
                self.myc.clear_old_cache_entries(by_atime=by_atime, hours=2)
                self.assertEqual(self.myc.cached_prop, 2)
                self.assertEqual(
                    self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2"
                )

        # Check clearance by access time.
        self.myc.calls.clear()
        self.myc.clear_cache()
        # Create new entries with current time.
        self.assertEqual(self.myc.cached_prop, 1)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")

        # Set access time to yesterday.
        with freeze_time(yesterday):
            self.assertEqual(self.myc.cached_prop, 1)
            self.assertEqual(
                self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
            )

        # Nothing cleared by creation time.
        self.myc.clear_old_cache_entries(by_atime=False, hours=2)
        with freeze_time(yesterday):
            self.assertEqual(self.myc.cached_prop, 1)
            self.assertEqual(
                self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
            )

        # All cleared by access time.
        self.myc.clear_old_cache_entries(by_atime=True, hours=2)
        self.assertEqual(self.myc.cached_prop, 2)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2")

        # Check clearance by creation time.
        self.myc.calls.clear()
        self.myc.clear_cache()
        # Create new entries yesterday.
        with freeze_time(yesterday):
            self.assertEqual(self.myc.cached_prop, 1)
            self.assertEqual(
                self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
            )

        # Update access time.
        self.assertEqual(self.myc.cached_prop, 1)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")

        # Nothing cleared by access time.
        self.myc.clear_old_cache_entries(by_atime=True, hours=2)
        self.assertEqual(self.myc.cached_prop, 1)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1")

        # All cleared by creation time.
        self.myc.clear_old_cache_entries(by_atime=False, hours=2)
        self.assertEqual(self.myc.cached_prop, 2)
        self.assertEqual(self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,2")

    def test_no_clear_new_cache_entries(self):
        """
        Old cache entries are cleared by age.
        """
        for by_atime in (True, False):
            self.myc.calls.clear()
            self.myc.clear_cache()
            with self.subTest(by_atime=by_atime):
                self.assertEqual(self.myc.cached_prop, 1)
                self.assertEqual(
                    self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
                )
                self.myc.clear_old_cache_entries(by_atime=by_atime, hours=2)
                self.assertEqual(self.myc.cached_prop, 1)
                self.assertEqual(
                    self.myc.cached_meth(1, 2, kwarg1=3), "cached_meth,1,2,3,1"
                )

    def test_sort_cached_method_values_by_atime(self):
        """
        Cached method values are sorted by access time.
        """
        meth_name = "cached_meth"
        meth = getattr(self.myc, meth_name)
        val1 = f"{meth_name},1,2,3,1"
        self.assertEqual(meth(1, 2, kwarg1=3), val1)
        self.assertEqual(meth(1, 2, kwarg1=4), "cached_meth,1,2,4,2")

        # pylint: disable=protected-access
        int_meth_name = self.myc._get_method_cache_name(meth_name)
        deq = self.myc._cache[int_meth_name]

        self.assertNotEqual(deq[0].value, val1)
        # Sleep to ensure that val1 has a more recent atime.
        time.sleep(0.001)
        self.assertEqual(deq[1].value, val1)

        # Sort one method.
        self.myc.sort_cached_method_values_by_atime("cached_meth")
        deq = self.myc._cache[int_meth_name]
        self.assertEqual(deq[0].value, val1)
        self.assertNotEqual(deq[1].value, val1)

        time.sleep(0.001)
        self.assertEqual(meth(1, 2, kwarg1=4), "cached_meth,1,2,4,2")

        # Sort all methods.
        self.myc.sort_cached_method_values_by_atime()
        deq = self.myc._cache[int_meth_name]
        self.assertNotEqual(deq[0].value, val1)
        self.assertEqual(deq[1].value, val1)

    def test_caching_method_maxsize(self):
        """
        Caching methods respect maxsize parameter.
        """
        count = 10
        for i in range(count):
            self.myc.cached_meth(i, i)
            self.myc.cached_meth_with_maxsize(i)

        # pylint: disable=protected-access
        deq1 = self.myc._cache[self.myc._get_method_cache_name(self.myc.cached_meth)]
        self.assertEqual(len(deq1), count)

        deq2 = self.myc._cache[
            self.myc._get_method_cache_name(self.myc.cached_meth_with_maxsize)
        ]
        self.assertEqual(len(deq2), 3)


if __name__ == "__main__":
    unittest.main()
