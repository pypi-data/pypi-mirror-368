import unittest

from obsender import senders


class DummySenderTestCase(unittest.TestCase):
    def test_without_params(self):
        senders.DummySender().send_metric('test.metric', 42)

    def test_with_params(self):
        senders.DummySender(host='test-host.localhost',
                            app_name='test_app',
                            logger=None,
                            timeout=10).send_metric('test.metric', 42)
