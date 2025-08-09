class SenderException(Exception):
    """Base Obsender Sender Exception"""


class SendMetricException(SenderException):
    """Metric failed to be sent"""


class SendEventException(SenderException):
    """Event failed to be sent"""
