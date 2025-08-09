import datetime
import functools
import logging
import sys

import six


LOG = logging.getLogger(__name__)


def skip_exceptions(log_level=logging.WARNING):
    def _decorator(method):
        @six.wraps(method)
        def _wrapper(self, metric_id, value, timestamp=None, logger=None,
                     timeout=None):
            try:
                return method(self, metric_id, value, timestamp, logger,
                              timeout)
            except Exception as e:
                msg = ('Failed to send metric'
                       ' (metric_id=%r, value=%r, timestamp=%r);'
                       ' reason: %r')
                (logger or self.logger).log(log_level,
                                            msg,
                                            metric_id, value, timestamp,
                                            e)
        return _wrapper
    return _decorator


def skip_event_exceptions(log_level=logging.WARNING):
    def _decorator(method):
        @six.wraps(method)
        def _wrapper(self, event_data, event_id=None, timestamp=None,
                     logger=None, timeout=None):
            try:
                return method(self, event_data, event_id, timestamp,
                              logger, timeout)
            except Exception as e:
                msg = ('Failed to send event data %r;'
                       ' reason: %r')
                (logger or self.logger).log(log_level,
                                            msg,
                                            event_data,
                                            e)
        return _wrapper
    return _decorator


def skip_metric_exceptions(log_level=logging.WARNING):
    def _decorator(method):
        @six.wraps(method)
        def _wrapper(self, metric_id, value, tags=None):
            try:
                return method(self, metric_id, value, tags)
            except Exception as e:
                msg = ('Failed to send metric'
                       ' (metric_id=%r, value=%r, tags=%r);'
                       ' reason: %r')
                self.logger.log(log_level,
                                msg,
                                metric_id, value, tags,
                                e)
        return _wrapper
    return _decorator


class BaseStepdownStrategy(object):

    _now = datetime.datetime.utcnow

    def __init__(self,
                 method,
                 exceptions,
                 error_limit=3,
                 error_period=datetime.timedelta(seconds=2 * 60),
                 stepdown_period=datetime.timedelta(seconds=5 * 60),
                 logger=None):
        super(BaseStepdownStrategy, self).__init__()

        self._method = method

        for exc_cls in exceptions:
            if not issubclass(exc_cls, Exception):
                raise TypeError(exc_cls)
        self._exceptions = tuple(exceptions)

        self._logger = logger or LOG

        self._error_limit = error_limit
        self._period = error_period
        self._stepdown_period = stepdown_period

        self._stepdown_end = None
        self._error_timestamps = []

    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, slf, *args, **kwargs):
        call_now = self._now()

        # cleanup outdated errors
        self._error_timestamps = [err_ts for err_ts in self._error_timestamps
                                  if (err_ts + self._period) >= call_now]

        # skip call or exit stepdown
        if self._stepdown_end is not None:
            if call_now <= self._stepdown_end:
                self._logger.warn('%s.%s(*%s, **%s) call was stepped down'
                                  ' for %s seconds until %s',
                                  type(slf).__name__, self._method.__name__,
                                  args, kwargs,
                                  self._stepdown_period.total_seconds(),
                                  self._stepdown_end)
                return
            self._stepdown_end = None

        try:
            result = self._method(slf, *args, **kwargs)
            self._error_timestamps = []  # reset stats
            return result
        except self._exceptions:
            exc_info = sys.exc_info()
            exc_now = self._now()
            self._error_timestamps.append(call_now)
            if len(self._error_timestamps) >= self._error_limit:
                self._stepdown_end = exc_now + self._stepdown_period
                self._error_timestamps = []
            six.reraise(*exc_info)


def stepdown(exceptions=None, strategy_cls=None, strategy_kwargs=None):
    if exceptions is None:
        exceptions = [Exception]

    if strategy_cls is None:
        strategy_cls = BaseStepdownStrategy
    if strategy_kwargs is None:
        strategy_kwargs = {}

    def decorator(method):
        s = strategy_cls(method, exceptions, **strategy_kwargs)
        functools.update_wrapper(s, method)
        return s

    return decorator
