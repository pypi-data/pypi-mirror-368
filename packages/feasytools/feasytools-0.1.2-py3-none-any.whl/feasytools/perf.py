from collections import defaultdict
from functools import wraps
import time


def time2str(tspan:float):
    tspan = round(tspan)
    s = tspan % 60
    m = tspan // 60 % 60
    h = tspan // 3600
    return f"{h:02}:{m:02}:{s:02}"


class _perf:
    RES = defaultdict(lambda: 0.0)

    def __call__(self, func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            _perf.RES[func.__name__] += execution_time
            return result

        return func_wrapper
    
    @property
    def results(self):
        return self.RES


FEasyTimer = _perf()


__all__ = ["FEasyTimer", "time2str"]