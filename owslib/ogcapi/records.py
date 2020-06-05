# =============================================================================
# Copyright (c) 2020 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging

from owslib.ogcapi.features import Features
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Records(Features):
    """Abstraction for OGC API - Records"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Features.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)
