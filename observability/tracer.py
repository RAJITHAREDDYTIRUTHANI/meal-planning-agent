"""
Tracing setup for observability
"""

import os
from typing import Optional
from functools import wraps
import time

# Simple tracer implementation (can be extended with OpenTelemetry)
class SimpleTracer:
    """Simple tracer for tracking agent operations"""
    
    def __init__(self):
        self.traces = []
        self.enabled = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    
    def start_span(self, operation_name: str, **attributes):
        """Start a new trace span"""
        if not self.enabled:
            return None
        
        span = {
            "operation": operation_name,
            "start_time": time.time(),
            "attributes": attributes,
            "events": []
        }
        self.traces.append(span)
        return span
    
    def add_event(self, span: Optional[dict], event_name: str, **attributes):
        """Add an event to a span"""
        if span and self.enabled:
            span["events"].append({
                "name": event_name,
                "time": time.time(),
                "attributes": attributes
            })
    
    def end_span(self, span: Optional[dict], **attributes):
        """End a trace span"""
        if span and self.enabled:
            span["end_time"] = time.time()
            span["duration"] = span["end_time"] - span["start_time"]
            span["attributes"].update(attributes)
            return span
        return None
    
    def get_traces(self):
        """Get all traces"""
        return self.traces
    
    def clear_traces(self):
        """Clear all traces"""
        self.traces = []


# Global tracer instance
_tracer: Optional[SimpleTracer] = None


def setup_tracer() -> SimpleTracer:
    """Set up tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = SimpleTracer()
    return _tracer


def get_tracer() -> SimpleTracer:
    """Get tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = setup_tracer()
    return _tracer


def trace_operation(operation_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            span = tracer.start_span(
                operation_name,
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            try:
                result = func(*args, **kwargs)
                tracer.end_span(span, success=True)
                return result
            except Exception as e:
                tracer.add_event(span, "error", error=str(e))
                tracer.end_span(span, success=False, error=str(e))
                raise
        return wrapper
    return decorator

