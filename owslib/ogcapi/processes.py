# =============================================================================
# Copyright (c) 2021 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging

import requests

from owslib.ogcapi import API
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Processes(API):
    """Abstraction for OGC API - Processes

    https://ogcapi.ogc.org/processes/overview.html
    """

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def processes(self) -> dict:
        """
        implements: GET /processes

        Lists the processes this API offers.

        WPS 1.0.0: GetCapabilities

        @returns: `dict` of available processes.
        """

        path = 'processes'
        return self._request(path)

    def process(self, process_id: str) -> dict:
        """
        implements: GET /processes/{process-id}

        Returns a detailed description of a process.

        WPS 1.0.0: DescribeProcess

        @returns: `dict` of a process description.
        """

        path = f'processes/{process_id}'
        return self._request(path)

    def process_jobs(self, process_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs

        Returns the running and finished jobs for a process (optional).

        @returns: `dict` of ....
        """

        path = f'processes/{process_id}/jobs'
        return self._request(path)

    def process_execute(self, process_id: str, json: dict) -> dict:
        """
        implements: POST /processes/{process-id}/jobs

        Executes a process, i.e. creates a new job. Inputs and outputs will have
        to be specified in a JSON document that needs to be send in the POST body.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs'
        return self._request_post(path, json)

    def _request_post(self, path: str, json: dict) -> dict:
        # TODO: needs to be implemented in base class
        url = self._build_url(path)

        response = requests.post(url, json=json)

        if response.status_code != requests.codes.ok:
            raise RuntimeError(response.text)

        return response.json()

    def process_status(self, process_id: str, job_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs/{job-id}

        Returns the status of a job of a process.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}'
        return self._request(path)

    def process_cancel(self, process_id: str, job_id: str) -> dict:
        """
        implements: DELETE /processes/{process-id}/jobs/{job-id}

        Cancel a job execution.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}'
        return self._request(path)

    def process_result(self, process_id: str, job_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs/{job-id}/results

        Returns the result of a job of a process.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}/results'
        return self._request(path)
