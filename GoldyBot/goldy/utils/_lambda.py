from typing import Callable

def is_lambda(_lambda: Callable) -> bool:
    """Returns true if the callable passed into this function is a lambda function."""
    base_lambda = lambda: None
    return isinstance(_lambda, type(base_lambda)) and _lambda.__name__ == base_lambda.__name__