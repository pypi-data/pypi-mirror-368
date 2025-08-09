#  coding=utf-8
#
#  Copyright 2023 VK Cloud.
#
#  All Rights Reserved.
#
#     Licensed under the Apache License, Version 2.0 (the "License"); you may
#     not use this file except in compliance with the License. You may obtain
#     a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#     WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#     License for the specific language governing permissions and limitations
#     under the License.

import time
import unittest

import mock

from obsender import senders

APP_NAME = "test_app_agent"
PREFIX = "apps.service"
FULL_PREFIX = "{}.{}".format(PREFIX, APP_NAME)
VICTORIA_METRICS_HOST = "127.0.0.1"
VICTORIA_METRICS_PORT = "8126"
OBSENDER_HOST = "compute1_compute_i"
METRIC = "test_metric"


def init_sender(app_name=APP_NAME, enabled=False, prefix=PREFIX,
                host=VICTORIA_METRICS_HOST, port=VICTORIA_METRICS_PORT,
                obsender_host=OBSENDER_HOST, **kwargs):
    return senders.VictoriaMetricSender(app_name=app_name,
                                        enabled=enabled,
                                        prefix=prefix,
                                        host=host,
                                        port=port,
                                        obsender_host=obsender_host,
                                        **kwargs)


class TestInitVictoriaMetricsSender(unittest.TestCase):

    def test_init(self):
        sender = init_sender(app_name="test.app-agent")

        self.assertEqual(APP_NAME, sender.app_name)

    def test_metric_prefix(self):
        sender = init_sender()

        self.assertEqual(FULL_PREFIX, sender.full_prefix)


class TestVictoriaMetricsSender(unittest.TestCase):

    def setUp(self):
        super(TestVictoriaMetricsSender, self).setUp()
        self.sender = init_sender()

    @mock.patch('obsender.vm_client.PushClient.incr')
    def test_increment(self, send_increment_mock):
        self.sender.send_increment(metric_id=METRIC, value=1)

        send_increment_mock.asseert_called_once_with(METRIC, 1)

    @mock.patch('obsender.vm_client.PushClient.incr')
    def test_decrement(self, send_increment_mock):
        self.sender.send_decrement(metric_id=METRIC, value=1)

        send_increment_mock.asseert_called_once_with(METRIC, -1)

    @mock.patch('obsender.vm_client.PushClient.gauge')
    def test_counter(self, send_counter_mock):
        self.sender.send_counter(metric_id=METRIC, value=1)

        send_counter_mock.asseert_called_once_with(METRIC, 1)

    @mock.patch('obsender.vm_client.PushClient.duration')
    def test_duration(self, send_duration_mock):
        cur_time = time.time()
        time_in_ms = cur_time * 1000
        self.sender.send_duration(metric_id=METRIC, value=cur_time)

        send_duration_mock.asseert_called_once_with(METRIC, time_in_ms)

    @mock.patch('obsender.vm_client.PushClient.incr')
    def test_skip_exceptions(self, send_counter_mock):
        send_counter_mock.side_effect = Exception()

        try:
            self.sender.send_increment(metric_id=METRIC, value=1)
        except Exception:
            self.fail("Send metric raised Exception unexpectedly!")
