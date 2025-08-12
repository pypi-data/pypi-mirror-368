import time
import pickle
import hashlib
import inspect
from pathlib import Path
from functools import partial, lru_cache

from .configure import config

CACHE_DIR = Path(config.cache_dir)
CACHE_QUERY = CACHE_DIR / 'query'

CACHE_QUERY.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=config.lru_capacity)
def get(cache_file):
    with open(cache_file, 'rb') as f:
        return pickle.load(f)


def flush(cache_file, func, *args, **kwargs):
    result = func(*args, **kwargs)
    with open(cache_file, 'wb') as file:
        pickle.dump(result, file)
    return result


def get_or_flush(cache_file, func, *args, **kwargs):
    try:
        return get(cache_file)
    except (pickle.UnpicklingError, EOFError, FileNotFoundError):
        return flush(cache_file, func, *args, **kwargs)


def cache_query(update=None, expire_seconds=86400):
    """缓存装饰器, 通过参数控制缓存更新逻辑

    Args:
        update (bool|None):
            - True: 强制更新缓存
            - False: 只要缓存存在就使用（忽略有效期）
            - None: 根据 `expire_seconds` 判断是否更新
        expire_seconds (int): 缓存有效期（秒）, 仅在 update=None 时生效
    """

    def decorator(func):
        def wrapper(*args, **kwargs):

            # 绑定参数生成唯一缓存键
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args_dict = bound_args.arguments
            sorted_args = sorted(args_dict.items(), key=lambda x: x[0])
            name = func.__name__ if not isinstance(func, partial) else func.func.__name__
            key_data = (name, sorted_args)

            # 计算哈希作为文件名
            hash_key = hashlib.sha256(pickle.dumps(key_data)).hexdigest()
            cache_file = CACHE_QUERY / f"{hash_key}.pkl"
            cache_exists = cache_file.exists()

            match update:
                case True:
                    return flush(cache_file, func, *args, **kwargs)

                case False:
                    if not cache_exists:
                        return flush(cache_file, func, *args, **kwargs)

                    return get_or_flush(cache_file, func, *args, **kwargs)

                case None:
                    if not cache_exists:
                        return flush(cache_file, func, *args, **kwargs)

                    if expire_seconds is not None:
                        current_time = time.time()
                        mtime = cache_file.stat().st_mtime
                        cache_valid = (current_time - mtime) <= expire_seconds
                    else:
                        cache_valid = True  # 无有效期要求

                    if not cache_valid:
                        return flush(cache_file, func, *args, **kwargs)

                    return get_or_flush(cache_file, func, *args, **kwargs)

                case _:
                    raise ValueError("Invalid update parameter value")

        return wrapper

    return decorator


__all__ = ['cache_query']
