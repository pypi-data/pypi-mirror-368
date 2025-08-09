from __future__ import unicode_literals

from re import compile
from re import sub

SANITIZE_METRIC_NAME_REGEX = (
    (compile('\\s+'), '_'),
    (compile('[/\\\\]'), '-'),
    (compile('[^\\w.-]'), ''),
)


def sanitize_metric_name(name):
    for regex, replacement in SANITIZE_METRIC_NAME_REGEX:
        name = sub(regex, replacement, name)
    return name


def env_bool(value):
    return value.lower() in {'1', 't', 'true'}
