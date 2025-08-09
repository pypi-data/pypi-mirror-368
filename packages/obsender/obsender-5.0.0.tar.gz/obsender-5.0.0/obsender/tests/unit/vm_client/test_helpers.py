from __future__ import unicode_literals

import pytest

from obsender.vm_client.helpers import sanitize_metric_name


@pytest.mark.parametrize(
    'passed, expected',
    (
        ('2-my-metric.is.ok', '2-my-metric.is.ok'),
        ('123', '123'),
        ('/got.some.\\slashes.in.mine', '-got.some.-slashes.in.mine'),
        ('no.offence.but.it  is.wrong', 'no.offence.but.it_is.wrong'),
    ),
)
def test_sanitize_metric_name(passed, expected):
    assert sanitize_metric_name(passed) == expected
