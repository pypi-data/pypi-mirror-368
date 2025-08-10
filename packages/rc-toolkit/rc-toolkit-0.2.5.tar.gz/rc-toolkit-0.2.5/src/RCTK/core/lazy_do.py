

from functools import wraps
from typing import Callable

class LazyCallable:
    def __init__(self, func, *args, **kw) -> None:
        self.__func = func
        self.__args = args
        self.__kw = kw
        
    
    def __getattr__(self, __name: str):
        func = self.__func
        self = func(*self.__args, **self.__kw)
        return getattr(self, __name)
    
    def __call__(self, *args, **kw):
        func = self.__func
        self = func(*args, **kw)
        return self

def lazy_do(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kw):
        return LazyCallable(func, *args, **kw)
    return wrapper

