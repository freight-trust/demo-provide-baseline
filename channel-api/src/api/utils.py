from functools import wraps
from flask import request


def form(func):
    @wraps(func)
    def wrapped(*args, **kwrags):
        return func(request.form.to_dict(), *args, **kwrags)
    return wrapped
