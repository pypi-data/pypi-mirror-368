#!/usr/bin/env python3
"""
Base class for all classes with cachable methods. This is required for classes
to work with the caching_property decoractor.
"""

import contextlib
import datetime
import functools
import inspect
import logging
import threading
from collections import deque

LOGGER = logging.getLogger(__name__)

# The alias datetime.UTC was only introduced in Python 3.11.
_UTC_TZ = datetime.timezone.utc


class _CachedProperty:  # pylint: disable=too-few-public-methods
    def __init__(self, value):
        self._value = value
        self.ctime = self._now()
        self.atime = None

    @staticmethod
    def _now():
        """
        The current time as a timezone-aware datetime object.
        """
        return datetime.datetime.now(_UTC_TZ)

    @property
    def value(self):
        """
        The value. This updates the access time.
        """
        self.atime = self._now()
        return self._value

    def is_older(self, delta, by_atime=True):
        """
        Check if the cached value older than a given age.

        Args:
            delta:
                A datetime.timedelta object representing the age limit.

            by_atime:
                If True, check the age of the last access time, else check the
                age of the creation time.

        Returns:
            A boolean indicating if the value is older than the given timedelta.
        """
        if by_atime:
            if self.atime is None:
                return False
            ref_time = self.atime
        else:
            ref_time = self.ctime
        return delta < (self._now() - ref_time)


class _CachedMethod(_CachedProperty):
    def __init__(self, value, args, kwargs):
        super().__init__(value)
        self.args = args
        self.kwargs = kwargs

    def same_args(self, arg_cmps, kwarg_cmps, args, kwargs):
        """
        Compare given arguments to those used to create the value.

        Args:
            arg_cmps:
                Comparison functions for positional arguments. These must be
                functions that accept 2 arguments and return a boolean to
                indicate if the arguments are considered equal. If a function is
                None then arguments will be compared using the default
                equivalence test (==).

            kwarg_cmps:
                Comparison functions for keyword arguments. These must map
                keyword argument names to comparision functions as described for
                arg_cmps.

            args:
                The positional arguments to compare.

            kwargs:
                The keyword arguments to compare.

        Returns:
            A boolean indicating if the arguments are equal.
        """
        if len(args) != len(self.args) or kwargs.keys() != self.kwargs.keys():
            return False

        for i, (prev_arg, new_arg) in enumerate(zip(self.args, args)):
            try:
                cmp_func = arg_cmps[i]
            except IndexError:
                cmp_func = None
            if (
                prev_arg != new_arg
                if cmp_func is None
                else not cmp_func(prev_arg, new_arg)
            ):
                return False

        for key, prev_arg in self.kwargs.items():
            new_arg = kwargs[key]
            cmp_func = kwarg_cmps.get(key)
            if (
                prev_arg != new_arg
                if cmp_func is None
                else not cmp_func(prev_arg, new_arg)
            ):
                return False

        return True


class Cachable:
    """
    Base class for all classes with cachable methods. This is required for
    classes to work with the caching_property decoractor.
    """

    def __init__(self):
        # A dict mapping names to 2-tuples of values and timestamps.
        self._cache = {}
        self._cache_lock = threading.RLock()

    @contextlib.contextmanager
    def _locked_cache(self):
        """
        Context manager for accessing the cache.
        """
        with self._cache_lock:
            yield self._cache

    @staticmethod
    def _get_property_cache_name(name):
        """
        Get the internal cache name for a property.

        Args:
            name:
                The property name.

        Returns:
            The internal name for caching the output of the property.
        """
        return f"property:{name}"

    @staticmethod
    def _get_method_cache_name(name):
        """
        Get the internal cache name for a method.

        Args:
            name:
                The method name or the method itself.

        Returns:
            The internal name for caching output of the method.
        """
        if not isinstance(name, str):
            name = name.__name__
        return f"method:{name}"

    @classmethod
    def caching_property(cls, method):
        """
        A decorator for class properties that cache results for subsequent
        calls.

        Args:
            cls:
                A subclass of this class.

            method:
                The method to convert to a caching property.

        Returns:
            A caching property.
        """
        name = method.__name__
        internal_name = cls._get_property_cache_name(name)

        @property
        @functools.wraps(method)
        def cmeth(self):
            # pylint: disable=protected-access
            with self._locked_cache() as cache:
                try:
                    cvalue = cache[internal_name]
                except KeyError:
                    LOGGER.debug('Generating output for "%s" property', name)
                    value = method(self)
                    cvalue = _CachedProperty(value)
                    cache[internal_name] = cvalue
                    # Return this way to update the internal access time.
                    return cvalue.value
                LOGGER.debug('Using cached output for "%s" property', name)
                return cvalue.value

        return cmeth

    def clear_cached_property(self, name):
        """
        Clear a specific property cache.

        Args:
            name:
                The property name.
        """
        with self._locked_cache() as cache:
            try:
                del cache[self._get_property_cache_name(name)]
            except KeyError:
                pass

    @classmethod
    def caching_method(cls, *arg_cmps, _cm_maxsize=None, **kwarg_cmps):
        """
        A decorator for class methods that cache results for subsequent calls.

        caution:
            This will internally store references to all arguments whenever the
            arguments are determined to be different from a previous set of
            arguments.

        Args:
            cls:
                A subclass of this class.

            *arg_cmps:
                Comparison functions for positional arguments. These must be
                functions that accept 2 arguments and return a boolean to
                indicate if the arguments are considered equal. If a function is
                None then arguments will be compared using the built-in id()
                function.

            _cm_maxsize:
                The maximum number of cached results to store for this method.
                If None, no maximum is imposed. Values of zero or less are
                equivalent to None.

            **kwarg_cmps:
                Comparison functions for keyword arguments. These must map
                keyword argument names to comparision functions as described for
                arg_cmps.

        Returns:
            A caching method decoractor.
        """

        maxsize = _cm_maxsize
        if maxsize is not None:
            try:
                maxsize = int(maxsize)
            except ValueError as err:
                raise ValueError(
                    "_cm_maxsize must be None or convertible to an int"
                ) from err
            if maxsize <= 0:
                maxsize = None

        def decorator(method):
            """
            Args:
                method:
                    The method to convert to a caching method.
            """
            name = method.__name__
            internal_name = cls._get_method_cache_name(name)

            signature = inspect.signature(method)

            @functools.wraps(method)
            def cmeth(self, *args, **kwargs):
                # Set positional and keyword arguments. Keyword arguments given
                # as positional arguments are converted to keyword arguments.
                last_pos_arg = 0
                name = None
                for i, (name, val) in enumerate(signature.parameters.items()):
                    if val.default is not inspect.Parameter.empty:
                        try:
                            # -1 because self is included in the signature but not in args
                            pos_arg = args[i - 1]
                        except IndexError:
                            kwargs.setdefault(name, val.default)
                        else:
                            if name in kwargs:
                                raise TypeError(
                                    f"{method.__name__}() got multiple values for argument '{name}'"
                                )
                            kwargs.setdefault(name, pos_arg)
                    else:
                        last_pos_arg = i
                args = args[:last_pos_arg]

                # pylint: disable=protected-access
                with self._locked_cache() as cache:
                    try:
                        cvalues = cache[internal_name]
                    except KeyError:
                        cvalues = deque([], maxsize)
                        cache[internal_name] = cvalues

                    for cvalue in cvalues:
                        if cvalue.same_args(arg_cmps, kwarg_cmps, args, kwargs):
                            LOGGER.debug('Using cached output for "%s" property', name)
                            return cvalue.value

                    LOGGER.debug('Generating output for "%s" method', name)
                    value = method(self, *args, **kwargs)
                    cvalue = _CachedMethod(value, args, kwargs)
                    cvalues.appendleft(cvalue)
                    # Return this way to update the internal access time.
                    return cvalue.value

            return cmeth

        return decorator

    def clear_cached_method(self, name):
        """
        Clear a specific method cache.

        Args:
            name:
                The method name or the method itself.
        """
        with self._locked_cache() as cache:
            try:
                del cache[self._get_method_cache_name(name)]
            except KeyError:
                pass

    def sort_cached_method_values_by_atime(self, name=None):
        """
        Sort cached method values by access time.

        Args:
            name:
                A method name or method object to sort. If None, all cached
                method values will be sorted.
        """
        with self._locked_cache() as cache:
            if name:
                name = self._get_method_cache_name(name)
                try:
                    deq = cache[name]
                except KeyError:
                    return
                cache[name] = deque(
                    sorted(deq, key=lambda x: x.atime, reverse=True), deq.maxlen
                )
                return
            for key, cvalues in cache.items():
                if isinstance(cvalues, deque):
                    cache[key] = deque(
                        sorted(cvalues, key=lambda x: x.atime, reverse=True),
                        cvalues.maxlen,
                    )

    def clear_cache(self):
        """
        Clear cached values.
        """
        with self._locked_cache() as cache:
            cache.clear()

    def clear_old_cache_entries(
        self, by_atime=True, properties=None, methods=None, **kwargs
    ):
        """
        Clear old cache entries by age.

        Args:
            by_atime:
                If True, clear entries with access times older thant he
                specified time, else clear entries with creation times older
                than the specified time.

            properties:
                An optional list of properties to clear. If neither properties
                nor methods are specified then the entire cache will be cleared
                of old entries.

            methods:
                An optional list of methods to clear. If neither properties nor
                methods are specified then the entire cache will be cleared of
                old entries.

            **kwargs:
                Keyword arguments for creating datetime.timedelta objects to
                specify the threshold age.
        """
        if not kwargs:
            raise ValueError("No keyword arguments given for datetime.timedelta.")
        delta = datetime.timedelta(**kwargs)

        if properties:
            properties = set(properties)

        if methods:
            methods = set(
                name if isinstance(name, str) else name.__name__ for name in methods
            )

        old_props = set()
        with self._locked_cache() as cache:
            for name, cvalue in cache.items():
                if isinstance(cvalue, _CachedProperty):
                    if properties is None or name in properties:
                        if cvalue.is_older(delta, by_atime=by_atime):
                            old_props.add(name)
                else:
                    if methods is None or name in methods:
                        # Cycle the deque by popping items left and appending
                        # valid ones back on the right.
                        for _ in range(len(cvalue)):
                            cval = cvalue.popleft()
                            if not cval.is_older(delta, by_atime=by_atime):
                                cvalue.append(cval)
            for old_prop in old_props:
                del cache[old_prop]
