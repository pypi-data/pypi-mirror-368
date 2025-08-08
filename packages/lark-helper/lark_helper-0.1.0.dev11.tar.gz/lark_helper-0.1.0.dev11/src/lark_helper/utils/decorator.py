import asyncio
import functools
import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def timing_monitor(func_name: str | None = None, log_level: str = "INFO"):
    """
    函数执行耗时监测装饰器，兼容同步和异步函数

    Args:
        func_name: 自定义函数名称，如果不提供则使用函数的实际名称
        log_level: 日志级别，默认为INFO

    Usage:
        @timing_monitor()
        def sync_function():
            pass

        @timing_monitor("自定义名称")
        async def async_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            """同步函数包装器"""
            name = func_name or func.__name__
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                log_message = f"函数 '{name}' 执行完成，耗时: {execution_time:.4f} 秒"
                getattr(logger, log_level.lower())(log_message)

                return result
            except Exception as e:
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                error_message = (
                    f"函数 '{name}' 执行失败，耗时: {execution_time:.4f} 秒，错误: {e!s}"
                )
                logger.error(error_message)
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            """异步函数包装器"""
            name = func_name or func.__name__
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                log_message = f"异步函数 '{name}' 执行完成，耗时: {execution_time:.4f} 秒"
                getattr(logger, log_level.lower())(log_message)

                return result
            except Exception as e:
                end_time = time.perf_counter()
                execution_time = end_time - start_time

                error_message = (
                    f"异步函数 '{name}' 执行失败，耗时: {execution_time:.4f} 秒，错误: {e!s}"
                )
                logger.error(error_message)
                raise

        # 判断是否为异步函数
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def simple_timing(func: Callable) -> Callable:
    """
    简化版耗时监测装饰器，直接使用无需参数

    Usage:
        @simple_timing
        def my_function():
            pass

        @simple_timing
        async def my_async_function():
            pass
    """
    return timing_monitor()(func)


# 示例使用
if __name__ == "__main__":
    # 测试同步函数
    @timing_monitor("同步测试函数")
    def sync_test():
        time.sleep(1)
        return "同步函数执行完成"

    # 测试异步函数
    @timing_monitor("异步测试函数")
    async def async_test():
        await asyncio.sleep(1)
        return "异步函数执行完成"

    # 测试简化版装饰器
    @simple_timing
    def simple_sync_test():
        time.sleep(0.5)
        return "简化版同步函数"

    @simple_timing
    async def simple_async_test():
        await asyncio.sleep(0.5)
        return "简化版异步函数"

    # 运行测试
    async def run_tests():
        print("开始测试...")

        # 测试同步函数
        result1 = sync_test()
        print(f"结果1: {result1}")

        # 测试异步函数
        result2 = await async_test()
        print(f"结果2: {result2}")

        # 测试简化版
        result3 = simple_sync_test()
        print(f"结果3: {result3}")

        result4 = await simple_async_test()
        print(f"结果4: {result4}")

        print("测试完成!")

    # 运行异步测试
    asyncio.run(run_tests())
