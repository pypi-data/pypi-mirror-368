"""
为类方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器

functools.lru_cache 和 cache 函数会保留对调用参数的强引用, 会影响这些参数正常的垃圾回收, 需要等待缓存
超过 max_size 后弹出或手动调用 cache_clear, 比较麻烦.
最常见的场景是作用在一般的类方法上, 保留参数 self 的引用后会影响整个类实例的垃圾回收

>>> from functools import cache
>>>
>>> class Test:
...     def __del__(self):
...         print('delete!')
...     def method(self):
...         ...
...     @cache
...     def method_cache(self):
...         ...
...
>>> Test().method()
delete!
>>> Test().method()
delete!
>>> Test().method_cache()  # 无法进行垃圾回收
>>> Test().method_cache()
>>> Test().method_cache()
>>> Test.method_cache.cache_clear()  # 需手动调用, 一次性删除所有实例的缓存 (即使还有其他实例处于正常生命周期内)
delete!
delete!
delete!

此处提供一个一般类方法的结果缓存装饰器, 提供实例级别的缓存 (为每个实例单独创建缓存空间).
通过将缓存内容作为每个类实例的属性进行存储 (类似于 functools.cached_property), 避免了影响类实例 self 的正常垃圾回收.
对于其他调用参数, 当类实例被回收后也会正常回收
"""

import functools
# import inspect
import keyword
import threading
from typing import Callable, Optional

# python >= 3.7.0
__version__ = '0.1.0'

__all__ = ['instance_cache']

_kwargs_mark = (object(),)


def instance_cache(max_size: Optional[int] = 128, cache_name: Optional[str] = None,
                   precise_cache: bool = True) -> Callable[[Callable], Callable]:
    """
    为类方法提供实例级的结果缓存, 不影响类实例正常垃圾回收的装饰器工厂

    :param max_size: 单个实例的缓存数量限制 (非所有实例共享), 为 None 时表示无限制 (默认为 128)
    :param cache_name: 缓存字典的属性名称, 注意同一个类里不同方法的缓存属性名称应当唯一, 否则会混乱
        (默认为 '_results_cached_' + 装饰器返回方法的 id)
    :param precise_cache: 是否以牺牲一些性能为代价, 使用更精确的参数缓存策略 (默认为 True)

    例:
    >>> from instance_cache import instance_cache
    >>>
    >>> class Test:
    ...     @instance_cache(cache_name='method_cached')
    ...     def method(self, x=1, y=2):
    ...         print('run')
    ...         ...  # 耗时操作
    ...         return 1
    ...     def __del__(self):
    ...         print('delete!')
    ...
    >>> foo = Test()
    >>> foo.method(1, 2)
    run
    1
    >>> foo.method(1, 2)  # 命中缓存, 不运行方法直接返回结果
    1
    >>> foo.method_cached.clear()  # 清空实例的结果缓存
    >>> del foo  # 会立刻进行垃圾回收
    delete!

    若指定 precise_cache 为 True, 则以下调用方式的参数均视为相同, 会命中同一缓存:
    foo.method()
    foo.method(1)
    foo.method(y=2)
    foo.method(1, 2)
    foo.method(x=1, y=2)
    foo.method(y=2, x=1)
    foo.method(1, y=2)
    反之 precise_cache 为 False 时, 只有完全相同的调用才会被视为相同, 但此时性能会显著提高
    建议内部接口使用 precise_cache=False, 对外接口使用 precise_cache=True

    该方法线程安全
    """
    if max_size is not None:
        if not isinstance(max_size, int):
            raise TypeError(f'max_size must be an integer or None, not {type(max_size)!r}')

    if cache_name is not None:
        if not isinstance(cache_name, str):
            raise TypeError(f'cache_name must be a string or None, not {type(cache_name)!r}')

    if cache_name is not None:
        if not cache_name.isidentifier() or keyword.iskeyword(cache_name):
            raise ValueError(f'invalid variable name: {cache_name}')

    if max_size is not None:
        if max_size < 0:
            # 不缓存
            def decorator(method):
                return method

            return decorator

    def decorator(method):
        if precise_cache:
            import inspect

            sig = inspect.signature(method)
        lock = threading.Lock()

        @functools.wraps(method)
        def cached_method(self, *args, **kwargs):
            # 获取线程锁
            with lock:
                if not hasattr(self, lock_name):
                    setattr(self, lock_name, threading.Lock())

            cache_lock = getattr(self, lock_name)

            # 获取缓存键
            if precise_cache:
                bound = sig.bind(self, *args, **kwargs)
                bound.apply_defaults()
                args1, kwargs1 = bound.args, bound.kwargs
                key = args1[1:]  # 去除 self
                if kwargs1:
                    key += _kwargs_mark
                    for k in sorted(kwargs1):
                        key += (k, kwargs1[k])
            else:
                key = args
                if kwargs:
                    key += _kwargs_mark
                    for item in kwargs.items():
                        key += item

            with cache_lock:
                # 获取缓存字典
                if not hasattr(self, cache_method_name):
                    setattr(self, cache_method_name, {})
                cache_dict = getattr(self, cache_method_name)
                if not isinstance(cache_dict, dict):
                    cache_dict = {}
                    setattr(self, cache_method_name, cache_dict)

                # 检查是否存在缓存
                if key in cache_dict:
                    value = cache_dict.pop(key)
                    cache_dict[key] = value  # 弹出再放入, 顺序调到最后
                    return value

            # 获取值
            value = method(self, *args, **kwargs)

            with cache_lock:
                # 检查是否存在缓存
                if key in cache_dict:
                    value = cache_dict.pop(key)
                    cache_dict[key] = value  # 弹出再放入, 顺序调到最后
                    return value

                # 缓存结果
                cache_dict[key] = value
                if max_size is not None:
                    while cache_dict and len(cache_dict) > max_size:
                        del cache_dict[next(iter(cache_dict))]

            return value

        if cache_name is not None:
            cache_method_name = cache_name
        else:
            cache_method_name = f'_results_cached_{id(cached_method)}'
        lock_name = f'_cache_lock_{id(cached_method)}'

        return cached_method

    return decorator
