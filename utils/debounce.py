
import time
import threading

def debounce(wait):
    """Decorator that will postpone a function's execution until after `wait` seconds
    have elapsed since the last time it was invoked."""
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            
            debounced.t = threading.Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator
