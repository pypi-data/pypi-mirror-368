from __future__ import annotations

from inspect import getfullargspec
from typing import Any, Callable


def ensure_decorated_class_method(
    fn: Callable[..., Any],
    decorator_name: str,
) -> None:
    """
    Ensure that the decorated function is an instance method of a class.

    Checks the function's signature to verify that 'self' is the first argument.
    If not, it raises a TypeError.

    :param fn: The function or coroutine method to validate.
    :param decorator_name: The name of the decorator that requires this check.
    :raises TypeError: If the function is not a class instance method.
    """
    argspec = getfullargspec(fn)

    if not argspec.args or argspec.args[0] != "self":
        raise TypeError(
            f"The '{decorator_name}' decorator can only be used on methods of a class."
        )


def ensure_cache_adapter(
    obj: object,
    cache_attr: str,
) -> None:
    """
    Ensure that the given object has the specified cache attribute.

    Checks if `obj` has an attribute named `cache_attr`. If the attribute is
    missing, raises an AttributeError indicating the problem.

    :param obj: The object to check for the cache attribute.
    :param cache_attr: The name of the cache attribute to look for.
    :raises AttributeError: If the attribute `cache_attr` does not exist on `obj`.
    """

    if not hasattr(obj, cache_attr):
        raise AttributeError(
            f"The provided cache attribute `{cache_attr}` does not exist."
        )


__all__ = (
    "ensure_decorated_class_method",
    "ensure_cache_adapter",
)
