import contextlib
import datetime
import inspect
import json
import logging
import numbers
import uuid
try:
    from time import monotonic
except ImportError:
    from monotonic import monotonic

import six

from obsender import exceptions


class DurationMixin(object):
    """Mixin to meter timedelta and send its metric for wrapped code"""

    @contextlib.contextmanager
    def send_duration(self, metric_id, method_name='send_metric', **kwargs):
        if not hasattr(self, method_name):
            raise exceptions.SendMetricException(
                'Method %s not found' % method_name
            )
        method = getattr(self, method_name)
        start_time = monotonic()
        try:
            yield
        finally:
            method(
                metric_id,
                (monotonic() - start_time),
                **kwargs
            )


class SenderLoggerAdapter(logging.LoggerAdapter):
    """Writes Sender info for each log entry"""

    def __init__(self, logger, sender):
        super(SenderLoggerAdapter, self).__init__(logger, {})
        self._sender = sender

    def process(self, msg, kwargs):
        _msg = ("[obsender_sender=%s host=%s, app_name=%s] %s"
                % (self._sender.__class__.__name__,
                   self._sender.host,
                   self._sender.app_name,
                   msg))
        return _msg, kwargs


def jsonify(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime.datetime) and obj.tzinfo is None:
        # TODO(d.burmistrov): make TZ conversion
        return obj.isoformat(sep='T') + 'Z'
    elif isinstance(obj, datetime.timedelta):
        return str(obj.total_seconds())
    else:
        raise TypeError(obj)


def stringify(obj):
    if isinstance(obj, six.string_types):
        return obj
    elif obj is None:
        raise TypeError("can't convert ambiguous value %r" % obj)
    elif isinstance(obj, bool):
        return str(obj).lower()
    elif isinstance(obj, numbers.Number):
        return str(obj)
    elif isinstance(obj, uuid.UUID):
        return jsonify(obj)
    elif isinstance(obj, (datetime.datetime, datetime.timedelta)):
        return jsonify(obj)
    elif isinstance(obj, (list, tuple, dict)):
        return json.dumps(obj, default=jsonify)
    elif inspect.isclass(obj):
        return '%s.%s' % (obj.__module__, obj.__name__)
    elif isinstance(obj, BaseException):
        return repr(obj)
    else:
        raise TypeError("can't convert unsupported value %r" % obj)


def floatify(obj):
    if isinstance(obj, numbers.Number):
        return float(obj)
    else:
        raise TypeError("Can't convert unsupported value %r" % obj)
