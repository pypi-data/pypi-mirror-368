import time
import pysick


_last_time = time.time()

def _dt():
    """
    Returns delta time (in seconds).
    Can be used in while-not-QUIT loops with pysick.clock.tick(pysick.clock.dt())
    """
    global _last_time
    current_time = time.time()
    dt = current_time - _last_time
    _last_time = current_time
    return dt  # You can return in seconds or multiply by 1000 if you need ms



def time_in(ms, func):
    """Raw tk's After Func()"""
    pysick.ingine._root.after(ms, func)

def tick(ms=None, CODE=None):
    if isinstance(ms, int):
        time.sleep(ms / 1000)
    elif isinstance(ms, str):
        raise ValueError('ms must be int')
    elif ms is None:
        if CODE is None:
            raise ValueError('Codes are in ep system')
        elif CODE == 'X_DELTA_TIME$ACTIVE':
            dt = _dt()
            time.sleep(dt)

