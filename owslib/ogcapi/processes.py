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
        implements /processses/{processId}

        @type process_id: string
        @param process_id: id of process

        @returns: `dict` of process description
        """

        path = f'processes/{process_id}'
        return self._request(path=path)

    def execute(self, process_id: str, inputs: dict, outputs: dict = {},
                response: str = 'document', async_: bool = False) -> dict:
        """
        implements /processes/{processId}/execution

        @type process_id: string
        @param process_id: id of process
        @type data: string
        @param data: request payload
        @type inputs: inputs
        @param inputs: input parameters
        @type outputs: outputs
        @param outputs: output parameters
        @type async_: bool
        @param outputs: whether to execute request in asychronous mode

        @returns: `dict` of response or URL reference to job
        """

        data = {}

        if inputs:
            data['inputs'] = inputs
        if outputs:
            data['outputs'] = outputs

        data['response'] = response

        if async_:
            self.headers['Prefer'] = 'respond-async'
        else:
            self.headers['Prefer'] = 'respond-sync'

        path = f'processes/{process_id}/execution'

        return self._request(method='POST', path=path, data=data)
