# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import API
from owslib.util import Authentication


class Deployments(API):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def deployments(self) -> dict:
        """ implements /deployments
        @returns: `dict` of deployments object
        """
        path = 'deployments'
        return self._request(path=path)

    def deployment(self, deployment_id: str) -> dict:
        """ implements /deployments/{deploymentId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @returns: `dict` of deployment metadata
        """
        path = f'deployments/{deployment_id}'
        return self._request(path=path)

    def deployment_create(self, data: str) -> bool:
        """ implements /deployments
        @type data: dict
        @param data: JSON object
        @returns: `dict` of deployment metadata
        """
        path = 'deployments'
        _ = self._request(path=path, data=data, method='POST')

        return True

    def deployment_update(self, deployment_id: str, data: str) -> bool:
        """ implements /deployments/{deploymentId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @type data: dict
        @param data: JSON object
        @returns: `dict` of deployment metadata
        """
        path = f'deployments/{deployment_id}'
        _ = self._request(path=path, data=data, method='PUT')

        return True

    def deployment_delete(self, deployment_id: str) -> bool:
        """ implements /deployments/{deploymentId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @returns: `dict` of deployment metadata
        """
        path = f'deployments/{deployment_id}'
        _ = self._request(path=path, method='DELETE')

        return True

    def deployment_list_deployed_systems(self, deployment_id: str) -> dict:
        """ implements /deployments/{deploymentId}/systems
        @type deployment_id: string
        @param deployment_id: id of deployment
        @returns: `dict` of systems in a particular deployment
        """
        path = f'deployments/{deployment_id}/systems'
        return self._request(path=path)

    def deployment_add_systems_to_deployment(self, deployment_id: str, data: str) -> bool:
        """ implements /deployments/{deploymentId}/systems
        @type deployment_id: string
        @param deployment_id: id of deployment
        @type data: dict
        @param data: JSON object
        @returns: `dict` of systems in a particular deployment
        """
        path = f'deployments/{deployment_id}/systems'
        _ = self._request(path=path, data=data, method='POST')

        return True

    def deployment_retrieve_system_from_deployment(self, deployment_id: str, system_id: str) -> dict:
        """ implements /deployments/{deploymentId}/systems/{systemId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of system metadata
        """
        path = f'deployments/{deployment_id}/systems/{system_id}'
        return self._request(path=path)

    def deployment_update_system_in_deployment(self, deployment_id: str, system_id: str, data: str) -> bool:
        """ implements /deployments/{deploymentId}/systems/{systemId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @type system_id: string
        @param system_id: id of system
        @type data: dict
        @param data: JSON object
        @returns: `dict` of system metadata
        """
        path = f'deployments/{deployment_id}/systems/{system_id}'
        _ = self._request(path=path, data=data, method='PUT')

        return True

    def deployment_delete_system_in_deployment(self, deployment_id: str, system_id: str) -> bool:
        """ implements /deployments/{deploymentId}/systems/{systemId}
        @type deployment_id: string
        @param deployment_id: id of deployment
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of system metadata
        """
        path = f'deployments/{deployment_id}/systems/{system_id}'
        _ = self._request(path=path, method='DELETE')

        return True

    def deployment_list_deployments_of_system(self, system_id: str) -> dict:
        """ implements /systems/{systemId}/deployments
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of deployments of a particular system
        """
        path = f'systems/{system_id}/deployments'
        return self._request(path=path)