import sys
import os
import time

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
get_runtime_root_dir = os.path.dirname(os.path.dirname(__current_script_path))
sys.path.append(get_runtime_root_dir)
print(get_runtime_root_dir)

from typing import List
from fuxi.utils.thread_helper import run_in_executor


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed search docs."""
    print(f"-----start: {texts[0]}")
    print(texts)
    time.sleep(5)
    print(f"-----end: {texts[0]}")
    return [[1232, 4545.4]]


async def aembed_documents(texts: List[str]) -> List[List[float]]:
    """Asynchronous Embed search docs."""
    return await run_in_executor(None, embed_documents, texts)


async def main(texts):
    aa = await aembed_documents(texts)
    # bb = await aembed_documents(texts)
    print(aa)
    print("-----------")
    # print(bb)


async def coroutine_wrapper(async_gen, args):
    try:
        return await async_gen(args)
    except ValueError:
        pass


if __name__ == '__main__':
    import asyncio, json
    from typing import AsyncGenerator, AsyncIterator

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # coro1 = coroutine_wrapper(main,["xxxxxxxxxxx---jj"])
    # coro2 = coroutine_wrapper(main, ["yyyyyyyyyyy---jj"])
    coro1 = main(["xxxxxxxxxxx---jj"])
    coro2 = main(["yyyyyyyyyyy---jj"])
    task1 = loop.create_task(coro1)
    task2 = loop.create_task(coro2)
    try:
        loop.run_until_complete(task1)
        loop.run_until_complete(task2)
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()
