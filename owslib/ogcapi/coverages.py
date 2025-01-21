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

    def coverage(self, collection_id: str, **kwargs: dict) -> BinaryIO:
        """
        implements /collection/{collectionId}/coverage/

        @type collection_id: string
        @param collection_id: id of collection
        @type properties: tuple | list
        @param properties: range subset
        @type subset: list or dict of tuples/lists
        @param subset:
            [(name, lower bound, upper bound)]
            [[name, lower bound, upper bound]]
            {name: (lower bound, upper bound)}
            {name: [lower bound, upper bound]}
        @type scale_size: list of tuples or dict
        @param scale_size: [(axis name, number)] | {axis name: number}
        @type scale_factor: int
        @param scale_factor: factor by which to scale the resulting coverage
        @type scale_axes: list of tuples or dict
        @param scale_axes: [(axis name, number)] | {axis name: number}
        @type datetime: tuple | list | str
        @param datetime:
            tuple or list of start/end datetimes, or as 'start/end' string
            start and end datetimes can be ".." for unbounded value

        @returns: coverage data
        """

        kwargs_ = {}

        if isinstance(kwargs.get('properties'), (tuple, list)):
            kwargs_['properties'] = ','.join([
                str(x) for x in kwargs['properties']
            ])

        for p in ['scale_axes', 'scale_size']:
            if p in kwargs:
                p2 = p.replace('_', '-')
                if isinstance(kwargs[p], (tuple, list)):
                    items = kwargs[p]
                elif isinstance(kwargs[p], dict):
                    items = [
                        (name, value)
                        for name, value
                        in kwargs[p].items()
                    ]
                else:
                    continue
                kwargs_[p2] = []
                kwargs_[p2] = ",".join(
                    f'{s[0]}({s[1]})'
                    for s in items
                )

        if 'scale_factor' in kwargs:
            scale_f = float(kwargs['scale_factor'])
            scale_i = int(scale_f)
            if scale_i == scale_f:
                kwargs_['scale-factor'] = scale_i
            else:
                kwargs_['scale-factor'] = scale_f

        if 'subset' in kwargs:
            subset_items = []
            subset_values = kwargs['subset']
            if isinstance(subset_values, (tuple, list)):
                subset_items = subset_values
            elif isinstance(subset_values, dict):
                subset_items = [
                    (name, *values)
                    for name, values
                    in subset_values.items()
                ]
            if subset_items:
                kwargs_['subset'] = ','.join([
                    f'{s[0]}({s[1]}:{s[2]})'
                    for s in subset_items
                ])

        if 'datetime' in kwargs:
            if isinstance(kwargs['datetime'], (tuple, list)):
                kwargs_['datetime'] = '/'.join(kwargs['datetime'][:2])
            else:
                kwargs_['datetime'] = str(kwargs['datetime'])

        path = f'collections/{collection_id}/coverage'

        return BytesIO(self._request(path=path, as_dict=False, kwargs=kwargs_))
