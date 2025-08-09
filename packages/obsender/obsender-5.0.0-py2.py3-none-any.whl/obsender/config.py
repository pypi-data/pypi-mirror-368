from oslo_config import cfg

from obsender import constants

# Config example
#
# [victoria_metrics]
# enabled = False
# host = "localhost"
# port = 8125
# global_tags = {}
# prefix = "apps.application_name.dev"
# obsender_host = "localhost"


victoria_metrics_opts = [
    cfg.BoolOpt('enabled',
                default=False,
                help="Enable sending of metrics to Victoria Metrics"),
    cfg.StrOpt('host',
               default=None,
               help="Destination host to send metrics"),
    cfg.StrOpt('prefix',
               default='',
               help=("Prefix of metrics. Should be "
                     "'apps.<application_name>.<environment>'")),
    cfg.IntOpt('port',
               default=8125,
               help="Destination port to send metrics"),
    cfg.DictOpt('global_tags',
                default=None,
                help="Global tags for metrics in Victoria Metrics"),
    cfg.StrOpt('obsender_host',
               default=None,
               help="Specifies host to send metrics for"),
]

# dpp_events_opts = [
#     cfg.BoolOpt('enabled',
#                 default=False,
#                 help="Enable sending of data to DPP"),
#     cfg.StrOpt('src_host',
#                default=None,
#                help="Determines host to send data for"),
#     cfg.StrOpt('dpp_url',
#                default='',
#                help="Determines Data Platform endpoint for data push"),
#     cfg.FloatOpt('timeout',
#                  default=constants.DEFAULT_TIMEOUT,
#                  help="Determines timeout for waiting data upload"),
# ]


CONF = cfg.CONF
CONF.register_opts(victoria_metrics_opts, constants.VICTORIA_METRICS_DOMAIN)
# CONF.register_opts(dpp_events_opts, constants.DPP_EVENTS_DOMAIN)
