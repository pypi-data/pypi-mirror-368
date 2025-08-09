import time
import threading
import os
import datetime
import itertools
import json
import traceback

class Monitor:
    """Central monitor that records function call events, exceptions and timing.
    Thread-safe and supports nested calls (parent-child relationship).
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._counter = itertools.count(1)
        # mapping call_id -> event (partial until exit)
        self._events_map = {}
        # completed events in chronological order
        self._events = []
        self._local = threading.local()

    def _now_iso(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'

    def enter(self, func_name, args_repr=None, kwargs_repr=None):
        """Register function start. Returns call_id."""
        with self._lock:
            call_id = next(self._counter)
        start_perf = time.perf_counter()
        start_time = self._now_iso()
        parent = None
        stack = getattr(self._local, 'stack', [])
        if stack:
            parent = stack[-1]
        event = {
            'id': call_id,
            'func': func_name,
            'start_time': start_time,
            'start_perf': start_perf,
            'end_time': None,
            'end_perf': None,
            'duration_ms': None,
            'args': args_repr,
            'kwargs': kwargs_repr,
            'exception': None,
            'traceback': None,
            'parent_id': parent,
            'thread_id': threading.get_ident(),
            'process_id': os.getpid()
        }
        with self._lock:
            self._events_map[call_id] = event
            # push to stack
            if not hasattr(self._local, 'stack'):
                self._local.stack = []
            self._local.stack.append(call_id)
        return call_id

    def exit(self, call_id, result_repr=None, exception=None, tb=None):
        """Register function end and finalize the event."""
        end_perf = time.perf_counter()
        end_time = self._now_iso()
        with self._lock:
            event = self._events_map.get(call_id)
            if not event:
                # Unknown call id, ignore
                return
            event['end_time'] = end_time
            event['end_perf'] = end_perf
            event['duration_ms'] = (end_perf - event['start_perf']) * 1000.0
            event['result'] = result_repr
            if exception is not None:
                event['exception'] = repr(exception)
                event['traceback'] = tb
            # move to completed list
            self._events.append(event)
            # remove from map
            del self._events_map[call_id]
            # pop stack if present
            stack = getattr(self._local, 'stack', [])
            try:
                if stack and stack[-1] == call_id:
                    stack.pop()
                else:
                    # call_id not at top — remove if present (robustness)
                    if call_id in stack:
                        stack.remove(call_id)
            except Exception:
                pass

    def snapshot(self):
        """Return a snapshot (dict) with events and a summary."""
        with self._lock:
            events_copy = list(self._events)  # shallow copy
        summary = self._compute_summary(events_copy)
        return {'events': events_copy, 'summary': summary, 'generated_at': self._now_iso()}

    def _compute_summary(self, events):
        total_calls = len(events)
        total_time = sum(e.get('duration_ms', 0.0) for e in events)
        by_func = {}
        for e in events:
            fn = e['func']
            by_func.setdefault(fn, {'count':0, 'total_ms':0.0, 'max_ms':0.0})
            by_func[fn]['count'] += 1
            d = e.get('duration_ms') or 0.0
            by_func[fn]['total_ms'] += d
            if d > by_func[fn]['max_ms']:
                by_func[fn]['max_ms'] = d
        # produce a list sorted by total_ms descending
        func_stats = [{'func':k, 'count':v['count'], 'total_ms':v['total_ms'], 'max_ms':v['max_ms']} for k,v in by_func.items()]
        func_stats.sort(key=lambda x: x['total_ms'], reverse=True)
        exceptions = [e for e in events if e.get('exception')]
        return {'total_calls': total_calls, 'total_time_ms': total_time, 'by_function': func_stats, 'exceptions_count': len(exceptions)}

    def dump_json(self, path):
        data = self.snapshot()
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2)
