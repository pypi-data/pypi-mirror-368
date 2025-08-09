import functools, inspect, asyncio, traceback, json
from .core import Monitor

# small helper to keep arg reprs under control
def _sanitize_args(args, kwargs, max_len=500):
    try:
        a = repr(args)
        k = repr(kwargs)
        combined = a + ' ' + k
        if len(combined) > max_len:
            return combined[:max_len] + '...'
        return combined
    except Exception:
        return '<unrepresentable args>'

# Default global monitor instance
global_monitor = Monitor()

def instrumented(monitor=None):
    """Decorator factory to provide specific Monitor instance."""
    if monitor is None:
        monitor = global_monitor

    def _decorator(func):
        return trace(func, monitor=monitor)
    return _decorator

def trace(func=None, *, monitor=None):
    """Main decorator; supports both sync and async functions."""
    if monitor is None:
        monitor = global_monitor

    if func is None:
        return lambda f: trace(f, monitor=monitor)

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            args_r = _sanitize_args(args, kwargs)
            call_id = monitor.enter(func.__qualname__, args_repr=args_r, kwargs_repr=None)
            try:
                result = await func(*args, **kwargs)
                monitor.exit(call_id, result_repr=repr(result)[:500])
                # real-time console log
                print(f"[pytracer] CALL {call_id} {func.__qualname__} done in {monitor._events[-1]['duration_ms']:.3f} ms") if monitor._events else None
                return result
            except Exception as e:
                tb = traceback.format_exc()
                monitor.exit(call_id, exception=e, tb=tb)
                print(f"[pytracer] EXC  {call_id} {func.__qualname__} -> {e}")  # console
                raise

        return async_wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_r = _sanitize_args(args, kwargs)
            call_id = monitor.enter(func.__qualname__, args_repr=args_r, kwargs_repr=None)
            try:
                result = func(*args, **kwargs)
                monitor.exit(call_id, result_repr=repr(result)[:500])
                # real-time console log
                print(f"[pytracer] CALL {call_id} {func.__qualname__} done in {monitor._events[-1]['duration_ms']:.3f} ms") if monitor._events else None
                return result
            except Exception as e:
                tb = traceback.format_exc()
                monitor.exit(call_id, exception=e, tb=tb)
                print(f"[pytracer] EXC  {call_id} {func.__qualname__} -> {e}")  # console
                raise
        return wrapper
