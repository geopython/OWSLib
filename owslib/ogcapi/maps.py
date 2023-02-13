# =============================================================================
# Copyright (c) 2022 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from io import BytesIO
import logging
from typing import BinaryIO

from owslib.ogcapi import Collections
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Maps(Collections):
    """Abstraction for OGC API - Maps"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Collections.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def maps(self) -> list:
        """
        implements /collections filtered on maps

        @returns: `list` of filtered collections object
        """

        maps_ = []
        collections_ = super().collections()

        for c_ in collections_['collections']:
            for l_ in c_['links']:
                if 'map' in l_['rel']:
                    maps_.append(c_['id'])
                    break

        return maps_

    def map(self, collection_id: str, **kwargs: dict) -> BinaryIO:
        """
        implements /collection/{collectionId}/map

        @type collection_id: string
        @param collection_id: id of collection
        @type bbox: list
        @param bbox: list of minx,miny,maxx,maxy
        @type bbox_crs: str
        @param bbox_crs: CRS of output map
        @type datetime_: string
        @param datetime_: time extent or time instant
        @type width: int
        @param width: width of output map
        @type height: int
        @param height: height of output map
        @type transparent: bool
        @param transparent: whether to apply transparecy to
                            output map (default=True)
        @type style: str
        @param style: style name

        @returns: map image
        """

        kwargs_ = {}

        if 'bbox' in kwargs:
            kwargs_['bbox'] = ','.join(list(map(str, kwargs['bbox'])))
        if 'bbox_crs' in kwargs:
            kwargs_['bbox-crs'] = kwargs['bbox_crs']
        if 'datetime_' in kwargs:
            kwargs_['datetime'] = kwargs['datetime_']

        kwargs_['width'] = kwargs.get('width', 800)
        kwargs_['height'] = kwargs.get('height', 600)

        kwargs_['transparent'] = str(kwargs.get('transparent', True)).lower()

        if 'style' in kwargs:
            path = f'collections/{collection_id}/styles/{kwargs["style"]}/map'
        else:
            path = f'collections/{collection_id}/map'

        return BytesIO(self._request(path=path, as_dict=False, kwargs=kwargs_))
