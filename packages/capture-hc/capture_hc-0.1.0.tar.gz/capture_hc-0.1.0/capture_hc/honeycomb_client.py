import libhoney
import time
from functools import wraps

class HoneycombClient:
    def __init__(self, writekey, dataset, debug=False):
        libhoney.init(writekey=writekey, dataset=dataset, debug=debug)
        self._client = libhoney

    def send_event(self, fields: dict):
        ev = self._client.new_event()
        for k, v in fields.items():
            ev.add_field(k, v)
        ev.send()
        self._client.flush()

    def timed(self, extra_fields=None, event_arg='event'):
        """
        Decorator to time a function and send a Honeycomb event.
        Passes a libhoney event object as a kwarg (default: 'event').
        Usage:
            @honey.timed({"alert_name": "my_func"})
            def my_func(..., event=None):
                event.add_field("key", value)
            
            @honey.timed({"alert_name": "my_func"}, event_arg='track')
            def my_func(..., track=None):
                track.add_field("key", value)
        """
        extra_fields = extra_fields or {}
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                ev = self._client.new_event()
                for k, v in extra_fields.items():
                    ev.add_field(k, v)
                kwargs[event_arg] = ev
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start) * 1000
                    ev.add_field("duration_ms", duration_ms)
                    ev.add_field("function_name", func.__name__)
                    ev.send()
                    self._client.flush()
            return wrapper
        return decorator
