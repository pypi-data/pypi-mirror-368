from functools import partial
from sys import stderr


def clean_up_empty_keywords(kwargs):
    keys = [k for k in kwargs]
    for key in keys:
        if not kwargs[key]:
            del kwargs[key]


def is_valid_kwargs(kwargs, key):
    return key in kwargs and kwargs[key]


printerr = partial(print, file=stderr)
