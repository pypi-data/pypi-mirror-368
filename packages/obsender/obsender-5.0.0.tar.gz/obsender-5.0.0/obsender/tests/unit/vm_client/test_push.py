from functools import partial
import socket

import pytest

from obsender.vm_client import PushClient

try:
    import mock
except ImportError:
    from unittest import mock


@pytest.fixture
def mock_sendto(monkeypatch):
    monkeypatch.setattr(socket, '_delegate_methods', [], raising=False)
    with mock.patch('socket.socket.sendto') as s:
        yield s


@pytest.fixture(autouse=True)
def mock_monotonic(monkeypatch):
    monkeypatch.setattr(
        'obsender.vm_client.push.monotonic', partial(next, iter([1.0, 2.0])))


@pytest.fixture
def client(monkeypatch, mock_sendto):
    monkeypatch.setenv('PUSH_METRICS_PREFIX', 'apps.services.local')
    monkeypatch.setenv('PUSH_METRICS_ENABLED', '1')

    client = PushClient.from_env()
    yield client


def test_client_disabled(monkeypatch, mock_sendto):
    monkeypatch.setenv('PUSH_METRICS_ENABLED', '0')
    client = PushClient.from_env()
    client.incr('foo')
    mock_sendto.assert_not_called()


def test_timer_ok(mock_sendto, client):
    with client.timer('do_transaction'):
        pass

    mock_sendto.assert_called_once_with(
        b'apps.services.local.do_transaction:1000.000000|ms',
        ('localhost', 8125),
    )


def test_incr(mock_sendto, client):
    client.decr('my.bucket.bugs.count', 9)

    mock_sendto.assert_called_once_with(
        b'apps.services.local.my.bucket.bugs.count:-9|c',
        ('localhost', 8125),
    )


def test_gauge(mock_sendto, client):
    client.gauge('my.bucket.bugs.gauge', 9)

    mock_sendto.assert_called_once_with(
        b'apps.services.local.my.bucket.bugs.gauge:9|g',
        ('localhost', 8125),
    )


def test_tag_ok(mock_sendto, client):
    client.incr('my.bucket.bugs.count', 9, env='stage', version=11)
    mock_sendto.assert_called_once_with(
        b'apps.services.local.my.bucket.bugs.count;env=stage;version=11:9|c',
        ('localhost', 8125),
    )


def test_tailed_timer_ok(mock_sendto, client):
    with client.timer('do_transaction', tailed=True):
        pass

    mock_sendto.assert_called_once_with(
        b'apps.services.local.do_transaction.ok:1000.000000|ms',
        ('localhost', 8125),
    )


def test_tailed_timer_fail(mock_sendto, client):
    with pytest.raises(ValueError):
        with client.timer('do_transaction', tailed=True):
            raise ValueError

    mock_sendto.assert_called_once_with(
        b'apps.services.local.do_transaction.fail:1000.000000|ms',
        ('localhost', 8125),
    )


def test_tailed_timer_custom_ok(mock_sendto, client):
    tail = 200
    with client.timer('do_transaction', tailed=True) as t:
        try:
            pass
        except ValueError:
            tail = 500
            raise
        finally:
            t.set_tail(tail)

    mock_sendto.assert_called_once_with(
        b'apps.services.local.do_transaction.200:1000.000000|ms',
        ('localhost', 8125),
    )


def test_tailed_timer_custom_fail(mock_sendto, client):
    tail = 200
    with pytest.raises(ValueError):
        with client.timer('do_transaction', tailed=True) as t:
            try:
                raise ValueError
            except ValueError:
                tail = 500
                raise
            finally:
                t.set_tail(tail)

    mock_sendto.assert_called_once_with(
        b'apps.services.local.do_transaction.500:1000.000000|ms',
        ('localhost', 8125),
    )
