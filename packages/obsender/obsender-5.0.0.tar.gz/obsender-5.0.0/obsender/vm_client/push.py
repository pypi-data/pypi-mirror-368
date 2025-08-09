from __future__ import unicode_literals

from itertools import starmap
import os

try:
    from time import monotonic
except ImportError:  # pragma: no cover
    from monotonic import monotonic

from .helpers import env_bool
from .helpers import sanitize_metric_name
from .protocol import NullProto
from .protocol import UdpProto

ENV_VARS = {
    'host': (str, 'PUSH_METRICS_HOST'),
    'port': (int, 'PUSH_METRICS_PORT'),
    'prefix': (str, 'PUSH_METRICS_PREFIX'),
    'enabled': (env_bool, 'PUSH_METRICS_ENABLED'),
}


class PushClient(object):
    def __init__(
        self,
        host='localhost',
        port=8125,
        enabled=False,
        prefix='',
        tags=None,
        protocol=UdpProto,
    ):
        self.prefix = prefix
        self.tags = tags or {}

        if not enabled:
            protocol = NullProto
        self.protocol = protocol(host, port)

    @classmethod
    def from_env(cls, **extra):
        kwargs = {}
        for x, (t, name) in ENV_VARS.items():
            if os.getenv(name):
                kwargs[x] = t(os.getenv(name))

        kwargs.update(extra)
        return cls(**kwargs)

    def incr(self, bucket, count=1, **tags):
        self.send(bucket, '{}|c'.format(count), **tags)

    def decr(self, bucket, count=1, **tags):
        self.incr(bucket, -count, **tags)

    def gauge(self, bucket, value=1, **tags):
        self.send(bucket, '{}|g'.format(value), **tags)

    def timer(
        self,
        bucket,  # type: str
        tailed=False,  # type: bool
        **tags  # type: str
    ):  # type: (...) -> Timer
        return Timer(self, bucket, tailed, **tags)

    def duration(self, bucket, value, **tags):
        # type: (str, float, ...) -> None
        """Sends duration in ms (float)."""

        self.send(bucket, '{:0.6f}|ms'.format(value), **tags)

    def send(self, bucket, value, **tags):
        metric = sanitize_metric_name(bucket)
        if self.tags or tags:
            tags_all = dict(self.tags, **tags)
            tags_str = ';'.join(
                sorted(starmap('{}={}'.format, tags_all.items()))
            )
            metric = '{};{}'.format(metric, tags_str)

        data = '{}.{}:{}'.format(self.prefix, metric, value)
        self.protocol.send(data.encode())


class Timer(object):
    tail = None
    tails = ('ok', 'fail')

    def __init__(
        self,
        client,  # type: PushClient
        bucket,  # type: str
        tailed,  # type: bool
        **tags  # type: str
    ):
        self.client = client
        self.bucket = bucket
        self.tailed = tailed
        self.tags = tags

    def __enter__(self):
        self.start = monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tailed:
            tail = self.tail or self.tails[bool(exc_type)]
            self.bucket = '{}.{}'.format(self.bucket, tail)

        elapsed = 1000.0 * (monotonic() - self.start)
        self.client.duration(self.bucket, elapsed, **self.tags)

    def set_tail(self, tail):  # type: (...) -> None
        """The only public method"""
        self.tail = tail
