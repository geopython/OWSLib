# =============================================================================
# Copyright (c) 2021 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

import logging
import time
from typing import Tuple

import requests

from owslib.ogcapi import API
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Processes(API):
    """Abstraction for OGC API - Processes

    * https://ogcapi.ogc.org/processes/overview.html
    * https://docs.opengeospatial.org/DRAFTS/18-062.html
    * https://app.swaggerhub.com/apis/geoprocessing/WPS-all-in-one/1.0-draft.6-SNAPSHOT
    """

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def processes(self) -> dict:
        """
        implements: GET /processes

        Lists the processes this API offers.

        @returns: `dict` of available processes.
        """

        path = 'processes'
        data = self._request(path)
        return data["processes"]

    def process_description(self, process_id: str) -> dict:
        """
        implements: GET /processes/{process-id}

        Returns a detailed description of a process.

        @returns: `dict` of a process description.
        """

        path = f'processes/{process_id}'
        return self._request(path)

    def job_list(self, process_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs

        Returns the running and finished jobs for a process (optional).

        @returns: `dict` of ....
        """

        path = f'processes/{process_id}/jobs'
        return self._request(path)

    def execute(self, process_id: str, json: dict) -> str:
        """
        implements: POST /processes/{process-id}/jobs

        Executes a process, i.e. creates a new job. Inputs and outputs will have
        to be specified in a JSON document that needs to be send in the POST body.

        @returns: `str` of the status location
        """

        path = f'processes/{process_id}/jobs'
        resp = self._request_post(path, json)
        data = resp.json()
        return resp.headers.get("Location", data["location"])

    def _request_post(self, path: str, json: dict) -> requests.Response:
        # TODO: needs to be implemented in base class
        url = self._build_url(path)

        resp = requests.post(url, json=json)

        if resp.status_code != requests.codes.ok:
            raise RuntimeError(resp.text)

        return resp

    def status(self, process_id: str, job_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs/{job-id}

        Returns the status of a job of a process.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}'
        return self._request(path)

    def cancel(self, process_id: str, job_id: str) -> dict:
        """
        implements: DELETE /processes/{process-id}/jobs/{job-id}

        Cancel a job execution.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}'
        return self._request(path)

    def result(self, process_id: str, job_id: str) -> dict:
        """
        implements: GET /processes/{process-id}/jobs/{job-id}/results

        Returns the result of a job of a process.

        @returns: `dict` of ...
        """

        path = f'processes/{process_id}/jobs/{job_id}/results'
        return self._request(path)

    def monitor_execution(self, process_id: str = None, job_id: str = None, location: str = None,
                          timeout: int = 3600, delta: int = 10) -> Tuple[dict, bool]:
        """
        Job polling of status URL until completion or timeout.

        If `location` is provided, it is used instead.

        @returns: results of the monitoring upon completion as `tuple` of (data, success?)
        """
        time.sleep(1)  # small delay to ensure process execution had a change to start before monitoring
        left = timeout
        once = True
        data = None
        while left >= 0 or once:
            if location:
                data = self._request(url=location)
            else:
                data = self.status(process_id, job_id)
            if data['status'] in ['running', 'succeeded']:
                break
            if data['status'] == 'failed':
                return data, False
            time.sleep(delta)
            once = False
            left -= delta
        return data, data['status'] == 'succeeded'
