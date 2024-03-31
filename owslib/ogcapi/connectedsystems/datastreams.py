# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections
from owslib.util import Authentication


class Datastreams(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def datastreams(self) -> dict:
        """
        implements /datastreams
        @returns: `dict` of datastreams object
        """

        path = 'datastreams'
        return self._request(path=path)

    def datastream(self, datastream_id: str) -> dict:
        """
        implements /datastreams/{datastreamId}
        @type datastream_id: string
        @param datastream_id: id of datastream
        @returns: `dict` of datastream metadata
        """

        path = f'datastreams/{datastream_id}'
        return self._request(path=path)

    def datastreams_of_system(self, system_id: str) -> dict:
        """
        implements /datastreams?systemId={systemId}
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of datastream metadata
        """

        path = f'datastreams?systemId={system_id}'
        return self._request(path=path)

    def datastream_create_in_system(self, system_id: str, data: str) -> dict:
        """
        implements /datastreams
        @type system_id: string
        @param system_id: id of system
        @type data: dict
        @param data: JSON object
        @returns: `dict` of datastream metadata
        """

        path = 'systems/{systemId}/datastreams'
        return self._request(path=path, data=data, method='POST')

    def datastream_update_description(self, datastream_id: str, data: str) -> dict:
        """
        implements /datastreams/{datastreamId}
        @type datastream_id: string
        @param datastream_id: id of datastream
        @type data: dict
        @param data: JSON object
        @returns: `dict` of datastream metadata
        """

        path = f'datastreams/{datastream_id}'
        return self._request(path=path, data=data, method='PUT')

    def datastream_delete(self, datastream_id: str) -> dict:
        """
        implements /datastreams/{datastreamId}
        @type datastream_id: string
        @param datastream_id: id of datastream
        @returns: `dict` of datastream metadata
        """

        path = f'datastreams/{datastream_id}'
        return self._request(path=path, method='DELETE')

    def datastream_retrieve_schema_for_format(self, datastream_id: str, obs_format: str, type_: str) -> dict:
        """
        implements /datastreams/{datastreamId}/schema
        @type datastream_id: string
        @param datastream_id: id of datastream
        @type obs_format: string
        @param obs_format: observation format
        @type type_: string
        @param type_: type of schema (one of: 'view', 'create', 'replace', 'update'

        @returns: `dict` of schema
        """
        q_params = {
            'obsFormat': obs_format
        }

        if type_ in ['view', 'create', 'replace', 'update']:
            q_params['type'] = type_

        path = f'datastreams/{datastream_id}/schema'
        return self._request(path=path, kwargs=q_params)

    def datastream_update_schema_for_format(self, datastream_id: str, data: str) -> dict:
        """
        implements /datastreams/{datastreamId}/schema
        @type datastream_id: string
        @param datastream_id: id of datastream
        @type data: dict
        @param data: JSON object

        @returns: `dict` of schema
        """

        path = f'datastreams/{datastream_id}/schema'
        return self._request(path=path, data=data, method='PUT')

    