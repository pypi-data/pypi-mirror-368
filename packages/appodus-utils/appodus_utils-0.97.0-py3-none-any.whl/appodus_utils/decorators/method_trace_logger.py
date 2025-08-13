import functools
import inspect
import traceback
from typing import Callable, Awaitable, Any

from kink import di

AsyncCallable = Callable[..., Awaitable]
from logging import Logger

logger: Logger = di['logger']


def method_trace_logger(func: AsyncCallable) -> AsyncCallable:
    @functools.wraps(func) # Preserves metadata
    async def _wrapper(*args, **kwargs) -> Awaitable[Any]:
        try:
            logger.debug(f"Calling function  {func}, with params {args} and {kwargs}")
            return_value = None
            if inspect.iscoroutinefunction(func):
                return_value = await func(*args, **kwargs)
            else:
                return_value = func(*args, **kwargs)
            logger.debug(f"Return value is {return_value}")

            return return_value
        except Exception as e:
            logger.exception(f"An error occurred: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            raise e

    return _wrapper
