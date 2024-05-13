# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================

import json
from datetime import datetime
from time import sleep

import pytest
import requests

from owslib.ogcapi.connectedsystems import Systems, Deployments, Datastreams, Observations, ControlChannels, Commands, \
    SystemEvents, SystemHistory, SamplingFeatures, Properties
from owslib.util import Authentication
from tests.utils import service_ok

NODE_TEST_OK_URL = 'http://localhost:8585/sensorhub/test'
TEST_URL = 'http://localhost:8585/sensorhub/api/'
auth = Authentication('admin', 'admin')
sml_headers = {'Content-Type': 'application/sml+json'}
json_headers = {'Content-Type': 'application/json'}
geojson_headers = {'Content-Type': 'application/geo+json'}

system_definitions = [
    {"type": "Feature",
     "properties": {
         "featureType": "http://www.w3.org/ns/sosa/Sensor",
         "uid": "urn:osh:sensor:testcase:001",
         "name": "Test Sensor 001"},
     "geometry": None},
    {"type": "Feature",
     "properties": {
         "featureType": "http://www.w3.org/ns/sosa/Sensor",
         "uid": "urn:osh:sensor:testcase:002",
         "name": "Test Sensor 002"},
     "geometry": None}
]
sys_sml_def = {
    "type": "SimpleProcess",
    "uniqueId": "urn:osh:sensor:testsmlsensor:001",
    "label": "Test SML Sensor",
    "description": "A Sensor created from an SML document",
    "definition": "http://www.w3.org/ns/ssn/Sensor"
}

sml_component = {
    "type": "SimpleProcess",
    "uniqueId": "urn:osh:sensor:testcomponent:001",
    "label": "Test Component",
    "description": "Test Component Description",
    "definition": "http://www.w3.org/ns/ssn/Sensor"
}

sml_procedure_test_system = {"type": "SimpleProcess",
                             "uniqueId": "urn:osh:sensor:testsensorwithcomponents:001",
                             "label": "Test Process/Datastream Sensor",
                             "description": "A Sensor created to test procedure/datastream creation",
                             "definition": "http://www.w3.org/ns/ssn/Sensor"}
sml_procedure = {
    "type": "SimpleProcess",
    "id": "123456789",
    "description": "Test Procedure inserted via OWSLib",
    "uniqueId": "urn:osh:sensor:testprocedureows:001",
    "label": "Test Procedure - OWSLib",
    "definition": "http://www.w3.org/ns/sosa/Procedure"
}


class TestSystems:
    systems_api = Systems(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})

    def test_system_collections(self):
        assert False

    def test_collection_queryables(self):
        assert False

    def test_collection_items(self):
        assert False

    def test_collection_item(self):
        assert False

    def test_collection_item_create(self):
        assert False

    def test_systems(self):
        list_systems = self.systems_api.systems()
        assert list_systems is not None

    def test_system(self):
        list_sys_by_id = self.systems_api.system('94n1f19ld7tlc')
        assert list_sys_by_id is not None

    def test_system_create(self):
        self.systems_api.headers = {'Content-Type': 'application/sml+json'}
        sml_str = json.dumps(sys_sml_def)
        post_systems = self.systems_api.system_create(sml_str)

        assert post_systems is not None

    def test_system_update(self):
        sml_desc_copy = sys_sml_def.copy()
        sml_desc_copy['description'] = 'Updated Description'
        sml_str = json.dumps(sml_desc_copy)
        self.systems_api.headers = {'Content-Type': 'application/sml+json'}
        post_systems = self.systems_api.system_update('blid74chqmses', sml_str)

        check_result = self.systems_api.system('blid74chqmses')
        print(check_result)
        assert check_result['properties']['description'] == 'Updated Description'

    def test_system_delete(self):
        res = self.systems_api.system_delete('blid74chqmses')
        assert len(res) == 0


@pytest.mark.skip("Not implemented by server")
class TestProcedures:
    systems_api = Systems(TEST_URL, auth=auth, headers=sml_headers)

    def test_procedures(self):
        assert False

    def test_procedure(self):
        assert False

    def test_procedure_create(self):
        assert False

    def test_procedure_update(self):
        assert False

    def test_procedure_delete(self):
        assert False


class TestDeployments:
    systems_api = Systems(TEST_URL, auth=auth, headers=sml_headers)
    deployment_api = Deployments(TEST_URL, auth=auth, headers=geojson_headers)
    deployment_definition = {
        "type": "Feature",
        "properties": {
            "featureType": "http://www.w3.org/ns/sosa/Deployment",
            "uid": "urn:osh:sensor:testdeployment:001",
            "name": "Test Deployment 001",
            "description": "A test deployment",
            "validTime": ["2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]
        },
        # "geometry": "POINT(-80.0 35.0)"
    }
    deployment_expected_id = "vssamsrio5eb2"

    def test_deployments(self):
        res = self.deployment_api.deployments()
        print(res)
        assert res['items'] is not None

    def test_deployment(self):
        res = self.deployment_api.deployment(self.deployment_expected_id)
        assert res is not None

    def test_deployment_create(self):
        res = self.deployment_api.deployment_create(json.dumps(self.deployment_definition))
        assert res is not None

    def test_deployment_update(self):
        self.deployment_definition['properties']['description'] = 'Updated Description of Deployment 001'
        res = self.deployment_api.deployment_update(self.deployment_expected_id, json.dumps(self.deployment_definition))
        assert res is not None

    def test_deployment_delete(self):
        res = self.deployment_api.deployment_delete(self.deployment_expected_id)
        assert res is not None

    def test_deployment_list_deployed_systems(self):
        res = self.deployment_api.deployment_list_deployed_systems(self.deployment_expected_id)
        assert False

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_add_systems_to_deployment(self):
        system_data = {
            "href": "http://localhost:8585/sensorhub/api/systems/blid74chqmses"
        }
        res = self.deployment_api.deployment_add_systems_to_deployment(self.deployment_expected_id,
                                                                       json.dumps(system_data), True)
        print(res)
        assert res is not None

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_retrieve_system_from_deployment(self):
        assert False

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_update_system_in_deployment(self):
        assert False

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_delete_system_in_deployment(self):
        assert False

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_list_deployments_of_system(self):
        assert False


class TestSamplingFeatures:
    systems_api = Systems(TEST_URL, auth=auth, headers=sml_headers)
    weatherstation_id = '0s2lbn2n1bnc8'
    sampling_feature_api = SamplingFeatures(TEST_URL, auth=auth, headers=geojson_headers,
                                            alternate_sampling_feature_url='featuresOfInterest')
    feature_def = {
        "geometry": {
            "type": "Point",
            "coordinates": [-80.0, 35.0]
        },
        "type": "Feature",
        "properties": {
            "featureType": "http://www.w3.org/ns/sosa/Station",
            "uid": "urn:osh:sensor:teststation:001",
            "name": "Test Station 001",
            "description": "A test station",
            "parentSystem@link": {"href": "http://localhost:8585/sensorhub/api/systems/blid74chqmses"},
            "sampledFeature@link": {
                "href": "https://data.example.com/link/to/resource",
                "rel": "alternate",
                "type": "application/json",
                "hreflang": "en-US",
                "title": "Resource Name",
                "uid": "urn:x-org:resourceType:0001",
                "rt": "http://www.example.org/uri/of/concept",
                "if": "http://www.opengis.net/spec/spec-id/version"}
        }
    }

    def test_sampling_features(self):
        res = self.sampling_feature_api.sampling_features()
        assert len(res['items']) > 0

    def test_sampling_feature(self):
        res = self.sampling_feature_api.sampling_feature('c4nce3peo8hvc')
        assert res['properties']['name'] == 'Station WS013'

    def test_sampling_feature_from_system(self):
        res = self.sampling_feature_api.sampling_features_from_system(self.weatherstation_id, use_fois=True)
        print(len(res['items']))
        assert len(res['items']) == 50

    def test_sampling_feature_create(self):
        self.systems_api.headers = sml_headers
        system_res = self.systems_api.system_create(json.dumps(sys_sml_def))
        new_sys_id = self.systems_api.systems(uid=sys_sml_def["uniqueId"])['items'][0]['id']
        print(f'System ID: {new_sys_id}')

        self.sampling_feature_api.headers = geojson_headers
        print(f'API Headers: {self.sampling_feature_api.headers}')
        res = self.sampling_feature_api.sampling_feature_create(new_sys_id, json.dumps(self.feature_def), True)
        assert self.sampling_feature_api.sampling_features_from_system(new_sys_id, use_fois=True)['items'] > 0

    def test_sampling_feature_update(self):
        self.sampling_feature_api.headers = geojson_headers
        self.feature_def['properties']['name'] = 'Updated Name'
        self.sampling_feature_api.sampling_feature_update('t69fod8tfa47u', json.dumps(self.feature_def))
        assert self.sampling_feature_api.sampling_feature('t69fod8tfa47u')['properties'][
                   'name'] == 'Updated Name'

    def test_sampling_feature_delete(self):
        res = self.sampling_feature_api.sampling_feature_delete('t69fod8tfa47u')
        print(res)
        assert res == {}


class TestProperties:
    def test_properties(self):
        assert False

    def test_property(self):
        assert False

    def test_property_create(self):
        assert False

    def test_property_update(self):
        assert False

    def test_property_delete(self):
        assert False


class TestDatastreams:
    ds_api = Datastreams(TEST_URL, auth=auth, headers=json_headers)
    sys_id = 'blid74chqmses'
    datastream_id = None
    ds_definition = {
        "name": "Test Datastream",
        "outputName": "Test Output #1",
        "schema": {
            "obsFormat": "application/swe+json",
            "encoding": {
                "type": "JSONEncoding",
                "vectorAsArrays": False
            },
            "recordSchema": {
                "type": "DataRecord",
                "label": "Test Datastream Record",
                "updatable": False,
                "optional": False,
                "definition": "http://test.com/Record",
                "fields": [
                    {
                        "type": "Time",
                        "label": "Test Datastream Time",
                        "updatable": False,
                        "optional": False,
                        "definition": "http://test.com/Time",
                        "name": "timestamp",
                        "uom": {
                            "href": "http://test.com/TimeUOM"
                        }
                    },
                    {
                        "type": "Boolean",
                        "label": "Test Datastream Boolean",
                        "updatable": False,
                        "optional": False,
                        "definition": "http://test.com/Boolean",
                        "name": "testboolean"
                    }
                ]
            }
        }
    }

    def test_datastreams(self):
        res = self.ds_api.datastreams()
        assert res is not None

    def test_datastream_creation_and_retrieval(self):
        # insert a datastream first
        self.ds_api.datastream_create_in_system(self.sys_id, json.dumps(self.ds_definition))
        ds_created = self.ds_api.datastreams_of_system(self.sys_id)
        assert ds_created['items'] is not None
        assert ds_created['items'][0]['name'] == 'Test Datastream'
        self.datastream_id = ds_created['items'][0]['id']

        res = self.ds_api.datastream(self.datastream_id)
        assert res['name'] == 'Test Datastream'

    @pytest.mark.skip("Covered by test_datastream_creation_and_retrieval")
    def test_datastreams_of_system(self):
        res = self.ds_api.datastreams_of_system(self.sys_id)
        assert res is not None

    @pytest.mark.skip("Covered by test_datastream_creation_and_retrieval")
    def test_datastream_create_in_system(self):
        res = self.ds_api.datastream_create_in_system(self.sys_id, json.dumps(self.ds_definition))
        assert res is not None

    def test_datastream_update_description(self):
        self.ds_definition['description'] = 'Updated Description of Datastream'
        res = self.ds_api.datastream_update_description(self.datastream_id, json.dumps(self.ds_definition))
        assert res is not None

    def test_datastream_delete(self):
        res = self.ds_api.datastream_delete(self.datastream_id)
        assert res is not None

    def test_datastream_retrieve_schema_for_format(self):
        res = self.ds_api.datastream_retrieve_schema_for_format(self.datastream_id)
        assert res is not None

    def test_datastream_update_schema_for_format(self):
        res = self.ds_api.datastream_update_schema_for_format(self.datastream_id, json.dumps(self.ds_definition))
        assert res is not None


class TestObservations:
    system_id = 'blid74chqmses'
    ds_id = None
    sys_api = Systems(TEST_URL, auth=auth, headers=sml_headers)
    ds_api = Datastreams(TEST_URL, auth=auth, headers=json_headers)
    obs_api = Observations(TEST_URL, auth=auth, headers=json_headers)
    the_time = datetime.utcnow().isoformat() + 'Z'

    ds_definition = {
        "name": "Test Datastream",
        "outputName": "Test Output #1",
        "schema": {
            "obsFormat": "application/swe+json",
            "encoding": {
                "type": "JSONEncoding",
                "vectorAsArrays": False
            },
            "recordSchema": {
                "type": "DataRecord",
                "label": "Test Datastream Record",
                "updatable": False,
                "optional": False,
                "definition": "http://test.com/Record",
                "fields": [
                    {
                        "type": "Time",
                        "label": "Test Datastream Time",
                        "updatable": False,
                        "optional": False,
                        "definition": "http://test.com/Time",
                        "name": "timestamp",
                        "uom": {
                            "href": "http://test.com/TimeUOM"
                        }
                    },
                    {
                        "type": "Boolean",
                        "label": "Test Datastream Boolean",
                        "updatable": False,
                        "optional": False,
                        "definition": "http://test.com/Boolean",
                        "name": "testboolean"
                    }
                ]
            }
        }
    }

    def test_observations(self):
        self.sys_api.headers = sml_headers
        self.sys_api.system_create(json.dumps(sys_sml_def))
        self.ds_api.datastream_create_in_system(self.system_id, json.dumps(self.ds_definition))
        self.ds_id = self.ds_api.datastreams_of_system(self.system_id)['items'][0]['id']
        print(f'ds_id: {self.ds_id}')

        observation = {
            "phenomenonTime": self.the_time,
            "resultTime": self.the_time,
            "result": {
                "timestamp": datetime.now().timestamp() * 1000,
                "testboolean": True
            }
        }
        self.obs_api.headers = {'Content-Type': 'application/om+json'}
        res = self.obs_api.observations_create_in_datastream(self.ds_id, json.dumps(observation))
        sleep(0.5)
        obs = self.obs_api.observations_of_datastream(self.ds_id)
        print(f'The Time: {self.the_time}')
        print(f'Obs: {obs}')
        assert obs['items'][0]['phenomenonTime'] == self.the_time

    @pytest.mark.skip("Covered by test_observations")
    def test_observation(self):
        assert False

    @pytest.mark.skip("Covered by test_observations")
    def test_observations_of_datastream(self):
        assert False

    @pytest.mark.skip("Covered by test_observations")
    def test_observations_create_in_datastream(self):
        assert False

    @pytest.mark.xfail(reason="Server appears to have an error not expected according to api spec")
    def test_observations_update(self):
        self.ds_id = self.ds_api.datastreams_of_system(self.system_id)['items'][0]['id']
        assert self.ds_id is not None
        observation = {
            "datastream@id": self.ds_id,
            "result": {
                "testboolean": False
            }
        }
        self.obs_api.headers = {'Content-Type': 'application/om+json'}
        obs = self.obs_api.observations_of_datastream(self.ds_id)['items'][0]
        print(f'Original Obs: {obs}')
        res = self.obs_api.observations_update(obs['id'], json.dumps(observation))
        obs = self.obs_api.observations_of_datastream(self.ds_id)['items'][0]
        print(f'Updated Obs: {obs}')
        assert obs['result']['testboolean'] is False

    def test_observations_delete(self):
        self.ds_id = self.ds_api.datastreams_of_system(self.system_id)['items'][0]['id']
        assert self.ds_id is not None
        obs = self.obs_api.observations_of_datastream(self.ds_id)['items'][0]
        print(f'Original Obs: {obs}')
        res = self.obs_api.observations_delete(obs['id'])
        obs = self.obs_api.observations_of_datastream(self.ds_id)
        print(f'Updated Obs: {obs}')
        assert obs['items'] == []


class TestControlChannels:
    def test_controls(self):
        assert False

    def test_control(self):
        assert False

    def test_controls_of_system(self):
        assert False

    def test_control_create_in_system(self):
        assert False

    def test_control_update(self):
        assert False

    def test_control_delete(self):
        assert False

    def test_control_retrieve_schema(self):
        assert False

    def test_control_update_schema(self):
        assert False


class TestCommands:
    def test_commands(self):
        assert False

    def test_command(self):
        assert False

    def test_commands_of_control_channel(self):
        assert False

    def test_commands_send_command_in_control_stream(self):
        assert False

    def test_commands_delete_command(self):
        assert False

    def test_commands_add_status_report(self):
        assert False

    def test_commands_retrieve_status_report(self):
        assert False

    def test_commands_update_status_report(self):
        assert False

    def test_commands_delete_status_report(self):
        assert False


class TestSystemEvents:
    system_id = 'blid74chqmses'
    sys_api = Systems(TEST_URL, auth=auth, headers=sml_headers)
    se_api = SystemEvents(TEST_URL, auth=auth, headers={'Content-Type': 'application/om+json'})
    system_event_def = {
        "resultTime": "2021-03-15T04:53:34Z",
        "result": 23.5
    }

    def test_system_events(self):
        assert False

    def test_system_events_of_specific_system(self):
        assert False

    def test_system_event_add_se_to_system(self):
        assert False

    def test_system_event(self):
        assert False

    def test_system_event_update(self):
        assert False

    def test_system_event_delete(self):
        assert False


class TestSystemHistory:
    def test_system_history(self):
        assert False

    def test_system_history_by_id(self):
        assert False

    def test_system_history_update_description(self):
        assert False

    def test_system_history_delete(self):
        assert False
