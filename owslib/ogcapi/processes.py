# =============================================================================
# Copyright (c) 2022 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging

from owslib.ogcapi import Collections
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Processes(Collections):
    """Abstraction for OGC API - Processes"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Collections.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def processes(self) -> list:
        """
        implements /processes

        @returns: `list` of available processes
        """

        path = 'processes'
        return self._request(path=path)['processes']

    def process(self, process_id: str) -> dict:
        """
        implements /processs/{processId}

        @type process_id: string
        @param process_id: id of process

        @returns: `dict` of process desceription
        """

        path = f'processes/{process_id}'
        return self._request(path=path)
