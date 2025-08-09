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

import logging

from obsender import senders

LOG = logging.getLogger(__name__)


def construct_senders(app_name, conf,
                      metric_sender_classes=None, event_sender_classes=None):
    metric_sender_classes = metric_sender_classes or [
        senders.VictoriaMetricSender,
    ]
    event_sender_classes = event_sender_classes or [senders.DPPSender]
    metric_senders = []
    for sender_class in metric_sender_classes:
        sender = sender_class.from_config(app_name=app_name, conf=conf)
        metric_senders.append(sender)

    event_senders = []
    for sender_class in event_sender_classes:
        sender = sender_class.from_config(app_name=app_name, conf=conf)
        event_senders.append(sender)

    return metric_senders, event_senders


class MultiSender(object):
    def __init__(self, metric_senders, event_senders):
        self.metric_senders = metric_senders
        self.event_senders = event_senders

    @classmethod
    def from_config(cls, app_name, conf,
                    metric_sender_classes=None, event_sender_classes=None):
        return cls(*construct_senders(app_name, conf, metric_sender_classes,
                                      event_sender_classes))

    def add_metric_sender(self, sender):
        self.metric_senders.append(sender)

    def add_event_sender(self, sender):
        self.event_senders.append(sender)

    def send_metric(self, metric_id, value, timestamp=None,
                    logger=None, timeout=None):
        for sender in self.event_senders:
            sender.send_metric(metric_id, value, timestamp, logger,
                               timeout)

    def send_event(self, event_data, timestamp=None, logger=None,
                   timeout=None):
        for sender in self.event_senders:
            sender.send_event(event_data=event_data,
                              timestamp=timestamp,
                              logger=logger,
                              timeout=timeout)

    def send_increment(self, metric_id, value, tags=None):
        for sender in self.metric_senders:
            sender.send_increment(metric_id, value, tags)

    def send_decrement(self, metric_id, value, tags=None):
        for sender in self.metric_senders:
            sender.send_decrement(metric_id, value, tags)

    def send_counter(self, metric_id, value, tags=None):
        for sender in self.metric_senders:
            sender.send_counter(metric_id, value, tags)

    def send_duration(self, metric_id, value, tags=None):
        for sender in self.metric_senders:
            sender.send_duration(metric_id, value, tags)


multi_sender = MultiSender([], [])


def init_singleton(app_name, conf,
                   metric_sender_classes=None, event_sender_classes=None):
    metric_senders, event_senders = construct_senders(
        app_name, conf, metric_sender_classes, event_sender_classes)
    for sender in metric_senders:
        multi_sender.add_metric_sender(sender)
    for sender in event_senders:
        multi_sender.add_event_sender(sender)
