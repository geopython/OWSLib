# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections
from owslib.util import Authentication


class Observations(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def observations(self) -> dict:
        """
        implements /observations
        @returns: `dict` of observations object
        """

        path = 'observations'
        return self._request(path=path)

    def observation(self, observation_id: str) -> dict:
        """
        implements /observations/{observationId}
        @type observation_id: string
        @param observation_id: id of observation
        @returns: `dict` of observation metadata
        """

        path = f'observations/{observation_id}'
        return self._request(path=path)

    def observations_of_datastream(self, datastream_id: str) -> dict:
        """
        implements /observations?datastreamId={datastreamId}
        @type datastream_id: string
        @param datastream_id: id of datastream
        @returns: `dict` of observations object
        """

        path = f'observations?datastreamId={datastream_id}'
        return self._request(path=path)

    def observations_create_in_datastream(self, datastream_id: str, data: str) -> dict:
        """
        implements /observations
        @type datastream_id: string
        @param datastream_id: id of datastream
        @type data: dict
        @param data: JSON object
        @returns: `dict` of observation metadata
        """

        path = f'datastreams/{datastream_id}/observations'
        return self._request(path=path, data=data, method='POST')

    def observations_update(self, observation_id: str, data: str) -> dict:
        """
        implements /observations/{observationId}
        @type observation_id: string
        @param observation_id: id of observation
        @type data: dict
        @param data: JSON object
        @returns: `dict` of observation metadata
        """

        path = f'observations/{observation_id}'
        return self._request(path=path, data=data, method='PUT')

    def observations_delete(self, observation_id: str) -> dict:
        """
        implements /observations/{observationId}
        @type observation_id: string
        @param observation_id: id of observation
        @returns: `dict` of observation metadata
        """
        path = f'observations/{observation_id}'
        return self._request(path=path, method='DELETE')
