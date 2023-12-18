# =============================================================================
# Copyright (c) 2023 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from io import BytesIO
import logging
from typing import BinaryIO

from owslib.ogcapi.features import Features
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class EnvironmentalDataRetrieval(Features):
    """Abstraction for OGC API - Environmental Data Retrieval"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Features.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def data(self) -> list:
        """
        implements /collections filtered on EDR data resources

        @returns: `list` of filtered collections object
        """

        datas = []
        collections_ = super().collections()

        for c_ in collections_['collections']:
            for l_ in c_['links']:
                if 'data' in l_['rel']:
                    datas.append(c_['id'])
                    break

        return datas

    def query_data(self, collection_id: str,
                   query_type: str, **kwargs: dict) -> BinaryIO:
        """
        implements /collection/{collectionId}/coverage/

        @type collection_id: string
        @param collection_id: id of collection
        @type query_type: string
        @param query_type: query type
        @type bbox: list
        @param bbox: list of minx,miny,maxx,maxy
        @type coords: string
        @param coords: well-known text geometry
        @type datetime_: string
        @type datetime_: string
        @param datetime_: time extent or time instant
        @type parameter_names: list
        @param parameter_names: list of parameter names

        @returns: coverage data
        """

        kwargs_ = {}

        if 'bbox' in kwargs:
            kwargs_['bbox'] = ','.join(list(map(str, kwargs['bbox'])))
        if 'parameter_names' in kwargs:
            kwargs_['parameter_names'] = ','.join(kwargs['parameter_names'])

        query_args_map = {
            'coords': 'coords',
            'corridor_width': 'corridor-width',
            'corridor_height': 'corridor-height',
            'crs': 'crs',
            'cube-z': 'cube-z',
            'datetime_': 'datetime',
            'height': 'height',
            'height_units': 'height-units',
            'resolution_x': 'resolution-x',
            'resolution_y': 'resolution-y',
            'resolution_z': 'resolution-z',
            'width': 'width',
            'width_units': 'width-units',
            'within': 'within',
            'z': 'z'
        }

        for key, value in query_args_map.items():
            if key in kwargs:
                kwargs_[value] = kwargs[key]

        path = f'collections/{collection_id}/{query_type}'

        return self._request(path=path, kwargs=kwargs_)
