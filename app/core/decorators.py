"""
Decorators script for Core module
"""
import functools
import logging
from time import perf_counter
from typing import Callable, Any

logger: logging.Logger = logging.getLogger(__name__)


def with_logging(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for logging
    :param func: function to be called
    :type func: Callable
    :return: Wrapped function
    :rtype: Any
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function for Logging decorator
        :param args: Arguments to be logged
        :type args: Any
        :param kwargs: Keyword arguments to be called
        :type kwargs: Any
        :return: The returned value from func
        :rtype: Any
        """
        logger.info("Calling %s", func.__name__)
        value = func(*args, **kwargs)
        logger.info("Finished %s", func.__name__)
        return value

    return wrapper


def benchmark(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Benchmark function for computational functions
    :param func: Function to be executed
    :type func: Callable
    :return: Wrapped function
    :rtype: Any
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function for benchmark decorator
        :param args: Arguments to be benchmarked
        :type args: Any
        :param kwargs: Keyword arguments to be called
        :type kwargs: Any
        :return: The returned value from func
        :rtype: Any
        """
        start_time: float = perf_counter()
        value = func(*args, **kwargs)
        end_time: float = perf_counter()
        run_time: float = end_time - start_time
        logger.info("Execution of %s took %s seconds.",
                    func.__name__, run_time)
        return value

    return wrapper
