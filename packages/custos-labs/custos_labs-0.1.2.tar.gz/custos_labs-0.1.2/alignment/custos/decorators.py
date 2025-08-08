# custos/decorators.py
import functools
from custos.exceptions import AlignmentViolation

def monitor(guardian):
    """
    Decorator to wrap an AI model's response generator.
    Automatically checks with custos guardian and logs to simulator.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(prompt, *args, **kwargs):
            response = func(prompt, *args, **kwargs)
            try:
                guardian.evaluate(prompt, response)
            except AlignmentViolation as e:
                print("[CUSTOS] Alignment Violation:", e)
            return response
        return wrapper
    return decorator