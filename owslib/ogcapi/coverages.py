# =============================================================================
# Copyright (c) 2020 Tom Kralidis
#
# Author: Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from io import BytesIO
import logging

from owslib.ogcapi import API
from owslib.util import Authentication

LOGGER = logging.getLogger(__name__)


class Coverages(API):
    """Abstraction for OGC API - Coverages"""

    def __init__(self, url: str, json_: str = None, timeout: int = 30,
                 headers: dict = None, auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def coverages(self) -> dict:
        """
        implements /collections filtered on coverages

        @returns: `dict` of filtered collections object
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

        path = 'collections/{}/coverage/domainset'.format(collection_id)
        return self._request(path=path, kwargs=kwargs)

    def coverage_rangetype(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/coverage/rangetype

        @type collection_id: string
        @param collection_id: id of collection

        @returns: coverage rangetype results
        """

        path = 'collections/{}/coverage/rangetype'.format(collection_id)
        return self._request(path=path, kwargs=kwargs)

    def coverage(self, collection_id: str, **kwargs: dict) -> dict:
        """
        implements /collection/{collectionId}/coverage/

        @type collection_id: string
        @param collection_id: id of collection
        @type range_subset: list
        @param range_subset: range subset
        @type subsets: list of tuples
        @param subsets: [(name, lower bound, upper bound)]

        @returns: coverage data
        """

        kwargs_ = {}

        if 'range_subset' in kwargs:
            kwargs_['rangeSubset'] = ','.join(
                [str(x) for x in kwargs['range_subset']])

        if 'subsets' in kwargs:
            kwargs_['subset'] = []
            for s in kwargs['subsets']:
                val = '{}({},{})'.format(s[0], s[1], s[2])
                kwargs_['subset'].append(val)

        path = 'collections/{}/coverage'.format(collection_id)

        return BytesIO(self._request(path=path, as_dict=False, kwargs=kwargs_))
