# =============================================================================
# Copyright (c) 2020 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging

from owslib.ogcapi.features import Features

LOGGER = logging.getLogger(__name__)


class Records(Features):
    """Abstraction for OGC API - Records"""

    def __init__(self, url, json_=None, timeout=30, headers=None, auth=None):
        __doc__ = Features.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)
