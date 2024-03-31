# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import API
from owslib.util import Authentication


class SamplingFeatures(API):
    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def sampling_features(self) -> dict:
        """
        implements /samplingFeatures
        @returns: `dict` of sampling features object
        """

        path = 'samplingFeatures'
        return self._request(path=path)

    def sampling_feature(self, sampling_feature_id: str) -> dict:
        """
        implements /samplingFeatures/{samplingFeatureId}
        @type sampling_feature_id: string
        @param sampling_feature_id: id of sampling feature
        @returns: `dict` of sampling feature metadata
        """

        path = f'samplingFeatures/{sampling_feature_id}'
        return self._request(path=path)

    def sampling_feature_from_system(self, system_id: str) -> dict:
        """
        implements /samplingFeatures?systemId={systemId}
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of sampling feature metadata
        """

        path = f'samplingFeatures?systemId={system_id}'
        return self._request(path=path)

    def sampling_feature_create(self, data: str) -> dict:
        """
        implements /samplingFeatures
        @type data: dict
        @param data: JSON object
        @returns: `dict` of sampling feature metadata
        """

        path = 'samplingFeatures'
        return self._request(path=path, data=data, method='POST')

    def sampling_feature_update(self, sampling_feature_id: str, data: str) -> dict:
        """
        implements /samplingFeatures/{samplingFeatureId}
        @type sampling_feature_id: string
        @param sampling_feature_id: id of sampling feature
        @type data: dict
        @param data: JSON object
        @returns: `dict` of sampling feature metadata
        """

        path = f'samplingFeatures/{sampling_feature_id}'
        return self._request(path=path, data=data, method='PUT')

    def sampling_feature_delete(self, sampling_feature_id: str) -> dict:
        """
        implements /samplingFeatures/{samplingFeatureId}
        @type sampling_feature_id: string
        @param sampling_feature_id: id of sampling feature
        @returns: `dict` of sampling feature metadata
        """

        path = f'samplingFeatures/{sampling_feature_id}'
        return self._request(path=path, method='DELETE')
