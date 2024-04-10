# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from owslib.ogcapi import Collections
from owslib.util import Authentication


class Commands(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def commands(self) -> dict:
        """
        implements /commands
        @returns: `dict` of commands object
        """

        path = 'commands'
        return self._request(path=path)

    def command(self, command_id: str) -> dict:
        """
        implements /commands/{commandId}
        @type command_id: string
        @param command_id: id of command
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}'
        return self._request(path=path)

    def commands_of_control_channel(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}/commands
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of commands object
        """

        path = f'controls/{control_id}/commands'
        return self._request(path=path)

    def commands_send_command_in_control_stream(self, control_id: str, data: str) -> dict:
        """
        implements /commands
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'controls/{control_id}/commands'
        return self._request(path=path, data=data, method='POST')

    def commands_delete_command(self, command_id: str) -> dict:
        """
        implements /commands/{commandId}
        @type command_id: string
        @param command_id: id of command
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}'
        return self._request(path=path, method='DELETE')

    def commands_add_status_report(self, command_id: str, data: str) -> dict:
        """
        implements /commands/{commandId}/status
        @type command_id: string
        @param command_id: id of command
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status'
        return self._request(path=path, data=data, method='POST')

    def commands_retrieve_status_report(self, command_id: str, status_id: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path)

    def commands_update_status_report(self, command_id: str, status_id: str, data: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @type data: dict
        @param data: JSON object
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path, data=data, method='PUT')

    def commands_delete_status_report(self, command_id: str, status_id: str) -> dict:
        """
        implements /commands/{commandId}/status/{statusId}
        @type command_id: string
        @param command_id: id of command
        @type status_id: string
        @param status_id: id of status
        @returns: `dict` of command metadata
        """

        path = f'commands/{command_id}/status/{status_id}'
        return self._request(path=path, method='DELETE')


class ControlChanels(Collections):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = Collections.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def controls(self) -> dict:
        """
        implements /controls
        @returns: `dict` of control channel objects
        """

        path = 'controls'
        return self._request(path=path)

    def control(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path)

    def controls_of_system(self, system_id: str) -> dict:
        """
        implements /systems/{system_id}/controls
        @type system_id: string
        @param system_id: id of system
        @returns: `dict` of control channels
        """

        path = f'systems/{system_id}/controls'
        return self._request(path=path)

    def control_create_in_system(self, system_id: str, data: str) -> dict:
        """
        implements /controls
        @type system_id: string
        @param system_id: id of system
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'systems/{system_id}/controls'
        return self._request(path=path, data=data, method='POST')

    def control_update(self, control_id: str, data: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path, data=data, method='PUT')

    def control_delete(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}'
        return self._request(path=path, method='DELETE')

    def control_retrieve_schema(self, control_id: str) -> dict:
        """
        implements /controls/{control_id}/schema
        @type control_id: string
        @param control_id: id of control channel
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}/schema'
        return self._request(path=path)

    def control_update_schema(self, control_id: str, data: str) -> dict:
        """
        implements /controls/{control_id}/schema
        @type control_id: string
        @param control_id: id of control channel
        @type data: dict
        @param data: JSON object
        @returns: `dict` of control channels
        """

        path = f'controls/{control_id}/schema'
        return self._request(path=path, data=data, method='PUT')


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


class Procedures(API):
    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__  # noqa
        super().__init__(url, json_, timeout, headers, auth)

    def procedures(self) -> dict:
        """
        implements /procedures
        @returns: `dict` of procedures object
        """

        path = 'procedures'
        return self._request(path=path)

    def procedure(self, procedure_id: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path)

    def procedure_create(self, data: str) -> dict:
        """
        implements /procedures
        @type data: dict
        @param data: JSON object
        @returns: `dict` of procedure metadata
        """

        path = 'procedures'
        return self._request(path=path, data=data, method='POST')

    def procedure_update(self, procedure_id: str, data: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @type data: dict
        @param data: JSON object
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path, data=data, method='PUT')

    def procedure_delete(self, procedure_id: str) -> dict:
        """
        implements /procedures/{procedureId}
        @type procedure_id: string
        @param procedure_id: id of procedure
        @returns: `dict` of procedure metadata
        """

        path = f'procedures/{procedure_id}'
        return self._request(path=path, method='DELETE')


class Properties(API):

    def __init__(self, url: str, json_: str = None, timeout: int = 30, headers: dict = None,
                 auth: Authentication = None):
        __doc__ = API.__doc__
        super().__init__(url, json_, timeout, headers, auth)

    def properties(self) -> dict:
        """
        implements /properties
        @returns: `dict` of properties object
        """

        path = 'properties'
        return self._request(path=path)

    def property(self, property_id: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path)

    def property_create(self, data: str) -> dict:
        """
        implements /properties
        @type data: dict
        @param data: JSON object
        @returns: `dict` of property metadata
        """

        path = 'properties'
        return self._request(path=path, data=data, method='POST')

    def property_update(self, property_id: str, data: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @type data: dict
        @param data: JSON object
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path, data=data, method='PUT')

    def property_delete(self, property_id: str) -> dict:
        """
        implements /properties/{propertyId}
        @type property_id: string
        @param property_id: id of property
        @returns: `dict` of property metadata
        """

        path = f'properties/{property_id}'
        return self._request(path=path, method='DELETE')


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
