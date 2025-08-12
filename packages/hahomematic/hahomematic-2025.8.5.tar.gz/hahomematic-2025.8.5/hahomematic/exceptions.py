"""Module for HaHomematicExceptions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
import inspect
import logging
from typing import Any, Final, cast

_LOGGER: Final = logging.getLogger(__name__)


class BaseHomematicException(Exception):
    """hahomematic base exception."""

    def __init__(self, name: str, *args: Any) -> None:
        """Init the HaHomematicException."""
        if args and isinstance(args[0], BaseException):
            self.name = args[0].__class__.__name__
            args = _reduce_args(args=args[0].args)
        else:
            self.name = name
        super().__init__(_reduce_args(args=args))


class ClientException(BaseHomematicException):
    """hahomematic Client exception."""

    def __init__(self, *args: Any) -> None:
        """Init the ClientException."""
        super().__init__("ClientException", *args)


class UnsupportedException(BaseHomematicException):
    """hahomematic unsupported exception."""

    def __init__(self, *args: Any) -> None:
        """Init the UnsupportedException."""
        super().__init__("UnsupportedException", *args)


class ValidationException(BaseHomematicException):
    """hahomematic validation exception."""

    def __init__(self, *args: Any) -> None:
        """Init the ValidationException."""
        super().__init__("ValidationException", *args)


class NoConnectionException(BaseHomematicException):
    """hahomematic NoConnectionException exception."""

    def __init__(self, *args: Any) -> None:
        """Init the NoConnection."""
        super().__init__("NoConnectionException", *args)


class NoClientsException(BaseHomematicException):
    """hahomematic NoClientsException exception."""

    def __init__(self, *args: Any) -> None:
        """Init the NoClientsException."""
        super().__init__("NoClientsException", *args)


class AuthFailure(BaseHomematicException):
    """hahomematic AuthFailure exception."""

    def __init__(self, *args: Any) -> None:
        """Init the AuthFailure."""
        super().__init__("AuthFailure", *args)


class HaHomematicException(BaseHomematicException):
    """hahomematic HaHomematicException exception."""

    def __init__(self, *args: Any) -> None:
        """Init the HaHomematicException."""
        super().__init__("HaHomematicException", *args)


class HaHomematicConfigException(BaseHomematicException):
    """hahomematic HaHomematicConfigException exception."""

    def __init__(self, *args: Any) -> None:
        """Init the HaHomematicConfigException."""
        super().__init__("HaHomematicConfigException", *args)


class InternalBackendException(BaseHomematicException):
    """hahomematic InternalBackendException exception."""

    def __init__(self, *args: Any) -> None:
        """Init the InternalBackendException."""
        super().__init__("InternalBackendException", *args)


def _reduce_args(args: tuple[Any, ...]) -> tuple[Any, ...] | Any:
    """Return the first arg, if there is only one arg."""
    return args[0] if len(args) == 1 else args


def log_exception[**P, R](
    exc_type: type[BaseException],
    logger: logging.Logger = _LOGGER,
    level: int = logging.ERROR,
    extra_msg: str = "",
    re_raise: bool = False,
    exc_return: Any = None,
) -> Callable:
    """Decorate methods for exception logging."""

    def decorator_log_exception(
        func: Callable[P, R | Awaitable[R]],
    ) -> Callable[P, R | Awaitable[R]]:
        """Decorate log exception method."""

        function_name = func.__name__

        @wraps(func)
        async def async_wrapper_log_exception(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap async methods."""
            try:
                return_value = cast(R, await func(*args, **kwargs))  # type: ignore[misc]
            except exc_type as exc:
                message = (
                    f"{function_name.upper()} failed: {exc_type.__name__} [{_reduce_args(args=exc.args)}] {extra_msg}"
                )
                logger.log(level, message)
                if re_raise:
                    raise
                return cast(R, exc_return)
            return return_value

        @wraps(func)
        def wrapper_log_exception(*args: P.args, **kwargs: P.kwargs) -> R:
            """Wrap sync methods."""
            return cast(R, func(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return async_wrapper_log_exception
        return wrapper_log_exception

    return decorator_log_exception
