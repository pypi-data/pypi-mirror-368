import abc
import contextlib
import datetime
import logging
import socket
import uuid

from concurrent import futures
# from dpp_client.clients import http
import obsender.vm_client as vm_client
# from requests import exceptions as requests_exceptions
import six

from obsender import common
from obsender import constants
from obsender import decorators
# from obsender import exceptions


DEFAULT_TIMEOUT = 10  # TODO(d.burmistrov): should be config option
LOG = logging.getLogger(__name__)


class BaseSenderMixin(object):
    _cfg_section = 'metrics'

    @classmethod
    def from_config(cls, app_name, conf, section=None):
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class AbstractSender(object):
    """The most basic Sender interface

    It shouldn't be subclassed directly - `AbstractBaseSender` should be used
    instead for any Real Sender.

    The only reason for subclassing `AbstractSender` is to create another base
    implementation with different strategy - like `AsyncSender`, it had
    completely different implementation from `AbstractBaseSender`.
    """

    @abc.abstractmethod
    def send_metric(self, metric_id, value, timestamp=None,
                    logger=None, timeout=None):
        pass

    @abc.abstractmethod
    def send_event(self, event_data, event_id=None, timestamp=None,
                   logger=None, timeout=None):
        pass


@six.add_metaclass(abc.ABCMeta)
class AbstractBaseSender(AbstractSender):
    """Base Sender class to be subclassed in Real Senders"""

    def __init__(self, host=None, app_name=None, logger=None, timeout=None):
        super(AbstractBaseSender, self).__init__()
        self.host = host or socket.getfqdn()
        self.app_name = app_name
        self.logger = common.SenderLoggerAdapter(logger or LOG, self)
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    @abc.abstractmethod
    def _send_metric(self, metric_id, value, timestamp, logger, timeout):
        pass

    def send_metric(self, metric_id, value, timestamp=None,
                    logger=None, timeout=None):
        timestamp = timestamp or datetime.datetime.utcnow()
        if self.app_name:
            metric_id = "%s.%s" % (self.app_name, metric_id)
        if timeout is None:
            timeout = self.timeout
        logger = logger or self.logger
        logger.debug('Sending metric metric_id=%s, value=%s, timestamp=%s',
                     metric_id, value, timestamp)
        self._send_metric(metric_id, value, timestamp, logger, timeout)

    @abc.abstractmethod
    def _send_event(self, event_data, logger, timeout):
        pass

    def send_event(self, event_data, event_id=None, timestamp=None,
                   logger=None, timeout=None):
        now = datetime.datetime.utcnow()
        if timestamp:
            event_data['timestamp'] = timestamp
        else:
            event_data.setdefault('timestamp', now)

        if event_id is not None:
            event_data['event_id'] = event_id
        else:
            event_data.setdefault('event_id', str(uuid.uuid4()))

        if self.app_name is not None:
            event_data.setdefault('app_name', self.app_name)
        event_data.setdefault('host', self.host)
        if timeout is None:
            timeout = self.timeout
        logger = logger or self.logger
        logger.debug('Sending event event_data=%s', event_data)
        self._send_event(event_data, logger, timeout)


class DummySender(AbstractBaseSender):
    """Dummy Sender to fake any real metric sending"""

    def _send_metric(self, metric_id, value, timestamp, logger, timeout):
        pass

    def _send_event(self, event_data, logger, timeout):
        pass


# Stub for DPP sender, it doesn't exist in public
class DPPSender(DummySender):
    def __init__(self, dpp_url, event_type=None, host=None, app_name=None,
                 logger=None, timeout=None, enforce_strings=False):
        super(DummySender, self).__init__()


# class DPPSender(BaseSenderMixin, AbstractBaseSender):
#     """Sender to send metrics into MCS Data Platform system"""

#     _ENFORCMENT_MSG = ('Enforcing event value to be'
#                        ' converted into string for DPP: %s')
#     _cfg_section = constants.DPP_EVENTS_DOMAIN

#     def __init__(self, dpp_url, event_type=None, host=None, app_name=None,
#                  logger=None, timeout=None, enforce_strings=False):
#         super(DPPSender, self).__init__(host, app_name, logger, timeout)
#         self._client = http.DPPClient(endpoint=dpp_url,
#                                       event_type=event_type or self.app_name,
#                                       timeout=timeout)
#         self.enforce_strings = enforce_strings

#     @classmethod
#     def from_config(cls, app_name, conf, section=None):
#         section = section or cls._cfg_section
#         return cls(
#             dpp_url=conf[section].dpp_url,
#             host=conf[section].src_host,
#             app_name=app_name,
#             timeout=conf[section].timeout,
#         )

#     def _send_metric(self, metric_id, value, timestamp, logger, timeout):
#         logger = logger or self.logger
#         logger.warning('DPPSender does not support sending metrics to DPP. '
#                        'This method will be removed in future releases.')

#     def send_metric(self, metric_id, value, timestamp=None,
#                     logger=None, timeout=None):
#         self._send_metric(metric_id, value, timestamp, logger, timeout)

#     def _format_event_data(self, event_data):
#         formatted_data = {}
#         with_enforced = False
#         for k, v in six.iteritems(event_data):
#             try:
#                 formatted_data[k] = common.stringify(v)
#             except TypeError as e:
#                 if not self.enforce_strings:
#                     raise
#                 self.logger.warning(self._ENFORCMENT_MSG, e)
#                 with_enforced = True
#                 formatted_data[k] = str(v)
#         if self.enforce_strings:
#             v = common.stringify(with_enforced)
#             formatted_data['obsender_forced_strings'] = v
#         return formatted_data

#     def _send_event(self, event_data, logger, timeout):
#         timestamp = event_data.pop('timestamp')
#         dpp_event_data = self._format_event_data(event_data)
#         event_type = dpp_event_data.pop('event_type', None)
#         try:
#             self._client.send_event(
#                 event_data=dpp_event_data,
#                 event_type=event_type,
#                 timestamp=timestamp,
#                 timeout=timeout,
#                 logger=logger)
#         except requests_exceptions.RequestException as e:
#             logger.exception('Failed to send event to DPP')
#             raise exceptions.SendEventException(e)


class AsyncSenderLoggerAdapter(logging.LoggerAdapter):
    """Writes Async Sender info for each log entry"""

    def __init__(self, logger, sender):
        super(AsyncSenderLoggerAdapter, self).__init__(logger, {})
        self._sender = sender

    def process(self, msg, kwargs):
        _msg = "[obsender_sender=%s] %s" % (
            self._sender.__class__.__name__, msg)
        return _msg, kwargs


class FSLoggerAdapter(logging.LoggerAdapter):
    """Writes Future ID for each log entry"""

    def __init__(self, logger, fs_uuid):
        super(FSLoggerAdapter, self).__init__(logger, {})
        self._fs_uuid = fs_uuid

    def process(self, msg, kwargs):
        return "[fs_uuid=%s] %s" % (self._fs_uuid, msg), kwargs


class AsyncSender(AbstractSender):
    """Sender that can use Real Sender in async manner

    Sends metrics in async manner using threading model. The real job is done
    by Real Sender. AsyncSender just wraps it with futures.
    """

    def __init__(self, concurrency_factor, sender, logger=None):
        super(AsyncSender, self).__init__()
        self.logger = AsyncSenderLoggerAdapter(logger or LOG, self)
        self.sender = sender
        self.concurrency_factor = concurrency_factor
        self._executor = futures.ThreadPoolExecutor(
            max_workers=self.concurrency_factor)
        self._fs = {}

    def _send_metric(self, metric_id, value, timestamp, logger, timeout):
        try:
            self.sender.send_metric(metric_id=metric_id,
                                    value=value,
                                    timestamp=timestamp,
                                    logger=logger,
                                    timeout=timeout)
            logger.debug("Metric send succeeded")
        except Exception:
            logger.exception("Metric send failed")

    def _send_event(self, event_data, event_id, logger, timeout):
        try:
            self.sender.send_event(event_data=event_data,
                                   event_id=event_id,
                                   logger=logger,
                                   timeout=timeout)
            logger.debug("Event send succeeded")
        except Exception:
            logger.exception("Event send failed")

    def _spawn_future(self, logger, f, **kwargs):
        fs_uuid = str(uuid.uuid4())
        self._fs[fs_uuid] = self._executor.submit(
            f, logger=FSLoggerAdapter(logger, fs_uuid), **kwargs)

    def send_metric(self, metric_id, value, timestamp=None,
                    logger=None, timeout=None):
        timestamp = timestamp or datetime.datetime.utcnow()
        self._spawn_future(logger or self.logger,
                           self._send_metric,
                           metric_id=metric_id,
                           value=value,
                           timestamp=timestamp,
                           timeout=timeout)

    def send_event(self, event_data, event_id=None, timestamp=None,
                   logger=None, timeout=None):
        now = datetime.datetime.utcnow()
        if timestamp:
            event_data['timestamp'] = timestamp
        else:
            event_data.setdefault('timestamp', now)
        self._spawn_future(logger or self.sender.logger,
                           self._send_event,
                           event_data=event_data,
                           event_id=event_id,
                           timeout=timeout)

    def wait_all(self):
        futures.wait(self._fs.values())
        self._fs = {}


class DurationMixin(object):
    """Mixin to meter timedelta and send its metric for wrapped code"""

    @contextlib.contextmanager
    def send_duration(self, metric_id):
        start = datetime.datetime.utcnow()
        yield
        duration = (datetime.datetime.utcnow() - start).total_seconds()
        self.send_metric(metric_id, duration)


class VictoriaMetricSender(BaseSenderMixin):
    """Sender to send metrics into VictoriaMetrics"""

    _cfg_section = constants.VICTORIA_METRICS_DOMAIN
    _ERR_MESSAGE = 'Failed to send {} metric to VictoriaMetrics'

    def __init__(self, app_name, enabled=False, prefix='', host=None,
                 port=8125, global_tags=None, obsender_host=None, logger=None):
        # victoria metrics can only accept underscores
        self.app_name = app_name.replace('-', '_').replace('.', '_')
        self.host = obsender_host or socket.getfqdn()
        self.full_prefix = self.app_name
        global_tags = global_tags or {}
        self.logger = common.SenderLoggerAdapter(logger or LOG, self)

        if prefix:
            self.full_prefix = '{}.{}'.format(prefix, self.full_prefix)
        self._client = vm_client.PushClient(
            host=host,
            port=port,
            enabled=enabled,
            prefix=self.full_prefix,
            tags=global_tags,
        )

    @classmethod
    def from_config(cls, app_name, conf, section=None):
        section = section or cls._cfg_section
        return cls(
            app_name=app_name,
            enabled=conf[section].enabled,
            prefix=conf[section].prefix,
            host=conf[section].host,
            port=conf[section].port,
            global_tags=conf[section].global_tags,
            obsender_host=conf[section].obsender_host,
        )

    @decorators.skip_metric_exceptions()
    @decorators.stepdown()
    def send_increment(self, metric_id, value=1, tags=None):
        tags = tags or {}
        self.logger.debug('Sending to bucket "%s" increment metric '
                          'metric_id=%s, value=%s',
                          self.full_prefix, metric_id, value)
        self._client.incr(metric_id, value, **tags)

    @decorators.skip_metric_exceptions()
    @decorators.stepdown()
    def send_decrement(self, metric_id, value=1, tags=None):
        tags = tags or {}
        self.logger.debug('Sending to bucket "%s" decrement metric '
                          'metric_id=%s, value=%s',
                          self.full_prefix, metric_id, value)
        self._client.decr(metric_id, value, **tags)

    @decorators.skip_metric_exceptions()
    @decorators.stepdown()
    def send_counter(self, metric_id, value=1, tags=None):
        tags = tags or {}
        self.logger.debug('Sending to bucket "%s" gauge metric '
                          'metric_id=%s, value=%s',
                          self.full_prefix, metric_id, value)
        self._client.gauge(metric_id, value, **tags)

    @decorators.skip_metric_exceptions()
    @decorators.stepdown()
    def send_duration(self, metric_id, value, tags=None):
        tags = tags or {}
        # Convert value to ms
        value_ms = common.floatify(value) * 1000.0
        self.logger.debug('Sending to bucket "%s" duration metric '
                          'metric_id=%s, value=%s',
                          self.full_prefix, metric_id, value_ms)
        self._client.duration(metric_id, value_ms, **tags)
