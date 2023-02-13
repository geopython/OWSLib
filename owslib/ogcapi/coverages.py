# =============================================================================
# Copyright (c) 2020 Tom Kralidis
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


class Coverages(Collections):
    """Abstraction for OGC API - Coverages"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = Collections.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def coverages(self) -> list:
        """
        implements /collections filtered on coverages

        @returns: `list` of filtered collections object
        """

        coverages_ = []
        collections_ = super().collections()

        for c_ in collections_['collections']:
            for l_ in c_['links']:
                if 'coverage' in l_['rel']:
                    coverages_.append(c_['id'])
                    break

        return coverages_

    def coverage_domainset(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/coverage/domainset

        @type collection_id: string
        @param collection_id: id of collection

        @returns: coverage domainset results
        """

        path = f'collections/{collection_id}/coverage/domainset'
        return self._request(path=path, kwargs=kwargs)

    def coverage_rangetype(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/coverage/rangetype

        @type collection_id: string
        @param collection_id: id of collection

        @returns: coverage rangetype results
        """

        path = f'collections/{collection_id}/coverage/rangetype'
        return self._request(path=path, kwargs=kwargs)

    def coverage(self, collection_id: str, **kwargs: dict) -> BinaryIO:
        """
        implements /collection/{collectionId}/coverage/

        @type collection_id: string
        @param collection_id: id of collection
        @type properties: list
        @param properties: range subset
        @type subset: list of tuples
        @param subset: [(name, lower bound, upper bound)]
        @type scale_size: list of tuples
        @param scale_size: [(axis name, number)]
        @type scale_factor: int
        @param scale_factor: factor by which to scale the resulting coverage
        @type scale_axes: list of tuples
        @param scale_axes: [(axis name, number)]

        @returns: coverage data
        """

        kwargs_ = {}

        if 'properties' in kwargs:
            kwargs_['properties'] = ','.join(
                [str(x) for x in kwargs['properties']])

        for p in ['scale_axes', 'scale_size']:
            if p in kwargs:
                p2 = p.replace('_', '-')
                kwargs_[p2] = []
                for s in kwargs[p2]:
                    val = f'{s[0]}({s[1]},{s[2]})'
                    kwargs_[p2].append(val)

        if 'subset' in kwargs:
            subsets_list = []
            for s in kwargs['subset']:
                subsets_list.append(f'{s[0]}({s[1]}:{s[2]})')
            kwargs['subset'] = ','.join(subsets_list)

        if 'scale_factor' in kwargs:
            kwargs_['scale-factor'] = int(kwargs['scale_factor'])

        path = f'collections/{collection_id}/coverage'

        return BytesIO(self._request(path=path, as_dict=False, kwargs=kwargs_))
