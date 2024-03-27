from concurrent.futures import ThreadPoolExecutor, as_completed, Executor
from typing import (
    Awaitable,
    List,
    Optional,
    Callable,
    Generator,
    Dict,
    Union,
    Any,
    TypeVar,
    cast,
)
from functools import partial
from contextvars import ContextVar, copy_context
import asyncio
from fuxi.utils.runtime_conf import get_log_verbose, logger
import logging
from typing_extensions import ParamSpec, TypedDict


def run_in_thread_pool(
        func: Callable,
        params: List[Dict] = [],
) -> Generator:
    """
    在线程池中批量运行任务，并将运行结果以生成器的形式返回。
    请确保任务中的所有操作是线程安全的，任务函数请全部使用关键字参数。
    """
    tasks = []
    with ThreadPoolExecutor() as pool:
        for kwargs in params:
            thread = pool.submit(func, **kwargs)
            tasks.append(thread)

        for obj in as_completed(tasks):  # TODO: Ctrl+c无法停止
            yield obj.result()


async def wrap_done(fn: Awaitable, event: asyncio.Event):
    """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
    try:
        await fn
    except Exception as e:
        logging.exception(e)
        msg = f"Caught exception: {e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if get_log_verbose() else None)
    finally:
        # Signal the aiter to stop.
        event.set()


P = ParamSpec("P")
T = TypeVar("T")


class RunnableConfig(TypedDict, total=False):
    """Configuration for a Runnable."""

    tags: List[str]
    """
    Tags for this call and any sub-calls (eg. a Chain calling an LLM).
    You can use these to filter calls.
    """

    metadata: Dict[str, Any]
    """
    Metadata for this call and any sub-calls (eg. a Chain calling an LLM).
    Keys should be strings, values should be JSON-serializable.
    """

    callbacks: Optional[Union[List, Any]]
    """
    Callbacks for this call and any sub-calls (eg. a Chain calling an LLM).
    Tags are passed to all callbacks, metadata is passed to handle*Start callbacks.
    """

    run_name: str
    """
    Name for the tracer run for this call. Defaults to the name of the class.
    """

    max_concurrency: Optional[int]
    """
    Maximum number of parallel calls to make. If not provided, defaults to 
    ThreadPoolExecutor's default.
    """

    recursion_limit: int
    """
    Maximum number of times a call can recurse. If not provided, defaults to 25.
    """

    configurable: Dict[str, Any]
    """
    Runtime values for attributes previously made configurable on this Runnable,
    or sub-Runnables, through .configurable_fields() or .configurable_alternatives().
    Check .output_schema() for a description of the attributes that have been made 
    configurable.
    """


async def run_in_executor(
        executor_or_config: Optional[Union[Executor, RunnableConfig]],
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
) -> T:
    """Run a function in an executor.

    Args:
        executor (Executor): The executor.
        func (Callable[P, Output]): The function.
        *args (Any): The positional arguments to the function.
        **kwargs (Any): The keyword arguments to the function.

    Returns:
        Output: The output of the function.
    """
    if executor_or_config is None or isinstance(executor_or_config, dict):
        # Use default executor with context copied from current context
        return await asyncio.get_running_loop().run_in_executor(
            None,
            cast(Callable[..., T], partial(copy_context().run, func, *args, **kwargs)),
        )

    return await asyncio.get_running_loop().run_in_executor(
        executor_or_config, partial(func, **kwargs), *args
    )
