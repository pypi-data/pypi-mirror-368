#!/usr/bin/env python3
"""
Base class for all registrable classes.
"""


import inspect
import logging

LOGGER = logging.getLogger(__name__)


class _RegistrableMetaClass(type):
    """
    Metaclass for Registrable to ensure that all classes that immediately derive
    from it define a register class attribute.
    """

    def __new__(mcs, name, bases, dct):
        for base in bases:
            if base.__name__ == "Registrable":
                dct[base._REGISTER_NAME] = {}
                break
        return super().__new__(mcs, name, bases, dct)


class Registrable(metaclass=_RegistrableMetaClass):
    """
    Base class for all registrable classes, i.e. classes that can be defined
    anywhere and registered into a central class register for use by the
    internal components of this library.

    To create a set of registrable classes, first devine a base class that
    derives from this class (e.g. EventMetric(Registrable),
    SequenceMetric(Registrable) and define a dict class attribute named
    _REGISTER in that base class. Define subclasses of that base class to create
    registrable subclasses.
    """

    # The name of the internal register attribute (a dict).
    _REGISTER_NAME = "_REGISTER"

    @classmethod
    def get_registration_base_class(cls):
        """
        Find the base class that contains the register. The base class should be
        a subclass of Registrable that defines a dict class attribute named
        _REGISTER (or whatever the value of _REGISTER_NAME is).

        Raises:
            ValueError:
                Failed to find a registration base class.
        """
        # Find the base class with the register.
        reg_name = cls._REGISTER_NAME
        reg_base_cls = None
        for base_cls in inspect.getmro(cls):
            if reg_name in base_cls.__dict__:
                reg_base_cls = base_cls
                break
        # Raise an error if the base class was not found.
        if reg_base_cls is None:
            raise ValueError(
                f"None of the base classes of {cls.__name__} contain "
                f"a dict class attribute named {reg_name}"
            )
        return reg_base_cls

    @classmethod
    def _get_register(cls):
        """
        Get the register.

        Returns:
            The register.
        """
        reg_cls = cls.get_registration_base_class()
        return getattr(reg_cls, cls._REGISTER_NAME)

    @classmethod
    def get_registration_name(cls, from_register=False):
        """
        Get the name of the class to use for registration. If the class's name
        contains the registration base class's name as a suffix, then the
        returned name will be the class's name without this suffix. For example,
        a class named "L2Metric" derived from a registrable base class "Metric"
        will return the string "L2".

        If the class's name does no include the base class's name as a suffix
        then the full name will be returned.

        Args:
            from_register:
                If True, check if the class already exists in the register and
                return the name under which it was registered. Use this to
                recover the names of previously registered classes.

        Returns:
            The registration name.
        """
        if from_register:
            for name, existing_cls in cls._get_register().items():
                if cls is existing_cls:
                    return name

        # Check that the registrable class follows the naming convention.
        expected_suffix = cls.get_registration_base_class().__name__
        if cls.__name__.endswith(expected_suffix):
            # Return the name without the suffix.
            return cls.__name__[: -len(expected_suffix)]
        return cls.__name__

    @classmethod
    def register(cls, name=None):
        """
        Register this class.

        Args:
            name:
                An optional name to use when registering the class. If not used,
                it will use the value returned by
                :py:meth:`~.Registrable.get_registration_name`
        """
        if name is None:
            name = cls.get_registration_name()
        elif not name or not isinstance(name, str):
            raise ValueError("The registration name must be a non-empty string.")

        reg_cls = cls.get_registration_base_class()
        reg = cls._get_register()

        try:
            old_cls = reg[name]
        except KeyError:
            LOGGER.debug(
                "Registering %s as subclass of %s with name %s.",
                cls.__qualname__,
                name,
                reg_cls.__qualname__,
            )
        else:
            LOGGER.warning(
                "Registering %s as subclass of %s with name %s [replaces %s].",
                cls.__qualname__,
                name,
                reg_cls.__qualname__,
                old_cls.__qualname__,
            )
        reg[name] = cls

    @classmethod
    def get_registered(cls, name):
        """
        Get a registered class.

        Args:
            name:
                The name of the registered class, as returned by get_name().

        Returns:
            The registered class.
        """
        try:
            return cls._get_register()[name]
        except KeyError as err:
            raise ValueError(
                f"No subclass of {cls.get_registration_base_class().__qualname__} "
                f"registered with name {name}"
            ) from err

    @classmethod
    def list_registered(cls):
        """
        List all of the currently registered names.

        Returns:
            A list of the registered names, sorted alphabetically.
        """
        return sorted(cls._get_register())

    @classmethod
    def list_registered_with_classes(cls):
        """
        List all of the currently registered names along with their classes.

        Returns:
            A list of 2-tuples of names-classes pairs, sorted alphabetically.
        """
        return sorted(cls._get_register().items())

    @classmethod
    def clear_registered(cls):
        """
        Clear all registered classes.
        """
        cls._get_register().clear()
