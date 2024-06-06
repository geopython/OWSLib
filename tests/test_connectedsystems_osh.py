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

from owslib.ogcapi.connectedsystems import Systems, Deployments, Datastreams, Observations, ControlChannels, Commands, \
    SystemEvents, SystemHistory, SamplingFeatures, Properties
from owslib.util import Authentication


class OSHFixtures:
    NODE_TEST_OK_URL = 'http://34.67.197.57:8585/sensorhub/test'
    # Directs to OSH hosted test server
    TEST_URL = 'http://34.67.197.57:8585/sensorhub/api/'
    auth = Authentication('auto_test', 'automated_tester24')
    sml_headers = {'Content-Type': 'application/sml+json'}
    json_headers = {'Content-Type': 'application/json'}
    geojson_headers = {'Content-Type': 'application/geo+json'}
    omjson_headers = {'Content-Type': 'application/om+json'}

    system_definitions = [
        {
            "type": "SimpleProcess",
            "uniqueId": "urn:osh:sensor:testsmlsensor:001",
            "label": "Test SML Sensor",
            "description": "A Sensor created from an SML document",
            "definition": "http://www.w3.org/ns/ssn/Sensor"
        },
        {
            "type": "SimpleProcess",
            "uniqueId": "urn:osh:sensor:testsmlsensor:002",
            "label": "Test SML Sensor #2",
            "description": "A Sensor created from an SML document",
            "definition": "http://www.w3.org/ns/ssn/Sensor"
        }
    ]

    sys_sml_to_update = {
        "type": "SimpleProcess",
        "uniqueId": "urn:osh:sensor:testsmlsensor:001",
        "label": "Test SML Sensor",
        "description": "A Sensor created from an SML document",
        "definition": "http://www.w3.org/ns/ssn/Sensor"
    }

    sys_sml_def = {
        "type": "SimpleProcess",
        "uniqueId": "urn:osh:sensor:testsmlsensor:solo",
        "label": "Test SML Sensor - Created on its own",
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
    system_id = 'blid74chqmses'
    deployment_expected_id = "vssamsrio5eb2"
    weatherstation_id = '0s2lbn2n1bnc8'
    datastream_id = 'etbrve0msmrre'

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

    systems_api = Systems(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    procedure_api = Systems(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    deployment_api = Deployments(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    sampling_feature_api = SamplingFeatures(TEST_URL, auth=auth, headers=geojson_headers,
                                            alternate_sampling_feature_url='featuresOfInterest')
    properties_api = Properties(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    datastream_api = Datastreams(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    observations_api = Observations(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    control_channels_api = ControlChannels(TEST_URL, auth=auth,
                                           headers={'Content-Type': 'application/json'})
    commands_api = Commands(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})
    system_events_api = SystemEvents(TEST_URL, auth=auth, headers=omjson_headers)
    system_history_api = SystemHistory(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})

    def update_dsid(self, ds_id):
        self.datastream_id = ds_id


class TestSystems:
    fixtures = OSHFixtures()

    @pytest.mark.skip("Not working on server implementation")
    def test_system_collections(self):
        assert False

    @pytest.mark.skip("Not working on server implementation")
    def test_collection_queryables(self):
        assert False

    @pytest.mark.skip("Not working on server implementation")
    def test_collection_items(self):
        assert False

    @pytest.mark.skip("Not working on server implementation")
    def test_collection_item(self):
        assert False

    @pytest.mark.skip("Not working on server implementation")
    def test_collection_item_create(self):
        assert False

    def test_system_functions(self):
        # insertion of systems
        self.fixtures.systems_api.headers = self.fixtures.sml_headers
        sys_create_res = self.fixtures.systems_api.system_create(json.dumps(self.fixtures.system_definitions))
        assert sys_create_res is not None

        # update of system and retrieval
        sml_desc_copy = self.fixtures.sys_sml_to_update.copy()
        sml_desc_copy['description'] = 'Updated Description'
        sml_str = json.dumps(sml_desc_copy)
        print(sml_str)
        post_systems = self.fixtures.systems_api.system_update('blid74chqmses', sml_str)
        print(post_systems)

        check_result = self.fixtures.systems_api.system('blid74chqmses')
        print(check_result)
        assert check_result['properties']['description'] == 'Updated Description'

        # deletion of system
        all_systems = self.fixtures.systems_api.systems()
        print(all_systems)

        # clear datastreams
        delete_all_datastreams()

        for system in all_systems['items']:
            print(f'System: {system}')
            res = self.fixtures.systems_api.system_delete(system['id'])
            print(f'res: {res}')
            assert res['code'] == 204


@pytest.mark.skip("Not implemented by server")
class TestProcedures:
    fixtures = OSHFixtures()

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
    fixtures = OSHFixtures()

    @pytest.mark.skip("Covered by test_deployment_create")
    def test_deployments(self):
        res = self.fixtures.deployment_api.deployments()
        print(res)
        assert self.fixtures.deployment_expected_id in [x['id'] for x in res['items']]

    @pytest.mark.skip("Covered by test_deployment_create")
    def test_deployment(self):
        res = self.fixtures.deployment_api.deployment(self.fixtures.deployment_expected_id)
        assert res['properties']['name'] == 'Test Deployment 001' and res['id'] == self.fixtures.deployment_expected_id

    def test_deployment_create(self):
        res1 = self.fixtures.deployment_api.deployment_create(json.dumps(self.fixtures.deployment_definition))
        assert res1
        res2 = self.fixtures.deployment_api.deployments()
        assert self.fixtures.deployment_expected_id in [x['id'] for x in res2['items']]
        res3 = self.fixtures.deployment_api.deployment(self.fixtures.deployment_expected_id)
        assert res3['properties']['name'] == 'Test Deployment 001' and res3[
            'id'] == self.fixtures.deployment_expected_id

    def test_deployment_update(self):
        self.fixtures.deployment_definition['properties']['description'] = 'Updated Description of Deployment 001'
        res = self.fixtures.deployment_api.deployment_update(self.fixtures.deployment_expected_id,
                                                             json.dumps(self.fixtures.deployment_definition))
        assert res is not None

    def test_deployment_delete(self):
        res = self.fixtures.deployment_api.deployment_delete(self.fixtures.deployment_expected_id)
        assert res is not None

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_list_deployed_systems(self):
        res = self.fixtures.deployment_api.deployment_list_deployed_systems(self.fixtures.deployment_expected_id)
        print(res)
        assert False

    @pytest.mark.skip("Not implemented by server")
    def test_deployment_add_systems_to_deployment(self):
        system_data = {
            "href": "http://localhost:8585/sensorhub/api/systems/blid74chqmses"
        }
        res = self.fixtures.deployment_api.deployment_add_systems_to_deployment(self.fixtures.deployment_expected_id,
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
    fixtures = OSHFixtures()

    def test_sampling_features(self):
        res = self.fixtures.sampling_feature_api.sampling_features()
        assert len(res['items']) > 0

    def test_sampling_feature(self):
        res = self.fixtures.sampling_feature_api.sampling_feature('c4nce3peo8hvc')
        assert res['properties']['name'] == 'Station WS013'

    def test_sampling_feature_from_system(self):
        res = self.fixtures.sampling_feature_api.sampling_features_from_system(self.fixtures.weatherstation_id,
                                                                               use_fois=True)
        print(len(res['items']))
        assert len(res['items']) == 50

    def test_sampling_feature_create(self):
        self.fixtures.systems_api.headers = self.fixtures.sml_headers
        system_res = self.fixtures.systems_api.system_create(json.dumps(self.fixtures.sys_sml_def))
        new_sys_id = self.fixtures.systems_api.systems(uid=self.fixtures.sys_sml_def["uniqueId"])['items'][0]['id']
        print(f'System ID: {new_sys_id}')

        self.fixtures.sampling_feature_api.headers = self.fixtures.geojson_headers
        print(f'API Headers: {self.fixtures.sampling_feature_api.headers}')
        res = self.fixtures.sampling_feature_api.sampling_feature_create(new_sys_id,
                                                                         json.dumps(self.fixtures.feature_def), True)
        assert len(
            self.fixtures.sampling_feature_api.sampling_features_from_system(new_sys_id, use_fois=True)['items']) > 0

    def test_sampling_feature_update(self):
        self.fixtures.sampling_feature_api.headers = self.fixtures.geojson_headers
        self.fixtures.feature_def['properties']['name'] = 'Updated Name'
        self.fixtures.sampling_feature_api.sampling_feature_update('t69fod8tfa47u',
                                                                   json.dumps(self.fixtures.feature_def))
        assert self.fixtures.sampling_feature_api.sampling_feature('t69fod8tfa47u')['properties'][
                   'name'] == 'Updated Name'

    def test_sampling_feature_delete(self):
        res = self.fixtures.sampling_feature_api.sampling_feature_delete('t69fod8tfa47u')
        print(res)
        assert res['code'] == 204


@pytest.mark.skip("Not implemented by server")
class TestProperties:
    fixtures = OSHFixtures()

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
    fixtures = OSHFixtures()

    def test_datastreams(self):
        res = self.fixtures.datastream_api.datastreams()
        assert res is not None

    def test_datastream_creation_and_retrieval(self):
        # insert a datastream first
        self.fixtures.datastream_api.datastream_create_in_system(self.fixtures.system_id,
                                                                 json.dumps(self.fixtures.ds_definition))
        ds_created = self.fixtures.datastream_api.datastreams_of_system(self.fixtures.system_id)
        assert ds_created['items'] is not None
        assert ds_created['items'][0]['name'] == 'Test Datastream'
        datastream_id = ds_created['items'][0]['id']
        self.fixtures.update_dsid(datastream_id)

        res = self.fixtures.datastream_api.datastream(datastream_id)
        assert res['name'] == 'Test Datastream'

    @pytest.mark.skip("Covered by test_datastream_creation_and_retrieval")
    def test_datastreams_of_system(self):
        res = self.fixtures.datastream_api.datastreams_of_system(self.fixtures.system_id)
        assert res is not None

    @pytest.mark.skip("Covered by test_datastream_creation_and_retrieval")
    def test_datastream_create_in_system(self):
        res = self.fixtures.datastream_api.datastream_create_in_system(self.fixtures.system_id,
                                                                       json.dumps(self.fixtures.ds_definition))
        assert res is not None

    @pytest.mark.xfail(reason="Server generates and error despite format of updated description being correct")
    def test_datastream_update_description(self):
        self.fixtures.ds_definition['description'] = 'Updated Description of Datastream'
        res = self.fixtures.datastream_api.datastream_update_description(self.fixtures.datastream_id,
                                                                         json.dumps(self.fixtures.ds_definition))
        res2 = self.fixtures.datastream_api.datastream(self.datastream_id)
        assert res2['description'] == 'Updated Description of Datastream'

    def test_datastream_retrieve_schema_for_format(self):
        res = self.fixtures.datastream_api.datastream_retrieve_schema_for_format(self.fixtures.datastream_id)
        print(f'Res: {res}')
        assert res is not None and len(res) > 0

    # Error due to server wanting PUT on main resource url, not ds/id/schema?
    @pytest.mark.xfail(
        reason="OSH doesn't separate schema from description so update fails with reference to update on main resource")
    def test_datastream_update_schema_for_format(self):
        res = self.fixtures.datastream_api.datastream_update_schema_for_format(self.fixtures.datastream_id,
                                                                               json.dumps(self.fixtures.ds_definition))
        print(f'Res: {res}')
        assert res is not None

    def test_datastream_delete(self):
        print(f'ds_id: {self.fixtures.datastream_id}')
        res = self.fixtures.datastream_api.datastream_delete(self.fixtures.datastream_id)
        print(res)
        assert res['code'] == 204


class TestObservations:
    fixtures = OSHFixtures()
    system_id = 'blid74chqmses'
    the_time = datetime.utcnow().isoformat() + 'Z'

    def test_observations(self):
        self.fixtures.systems_api.headers = self.fixtures.sml_headers
        self.fixtures.systems_api.system_create(json.dumps(self.fixtures.sys_sml_def))
        self.fixtures.datastream_api.datastream_create_in_system(self.fixtures.system_id,
                                                                 json.dumps(self.fixtures.ds_definition))
        self.fixtures.ds_id = self.fixtures.datastream_api.datastreams_of_system(self.fixtures.system_id)['items'][0][
            'id']
        print(f'ds_id: {self.fixtures.ds_id}')

        observation = {
            "phenomenonTime": self.the_time,
            "resultTime": self.the_time,
            "result": {
                "timestamp": datetime.now().timestamp() * 1000,
                "testboolean": True
            }
        }
        self.fixtures.observations_api.headers = {'Content-Type': 'application/om+json'}
        res = self.fixtures.observations_api.observations_create_in_datastream(self.fixtures.ds_id,
                                                                               json.dumps(observation))
        sleep(0.5)
        obs = self.fixtures.observations_api.observations_of_datastream(self.fixtures.ds_id)
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
        self.fixtures.ds_id = self.fixtures.datastream_api.datastreams_of_system(self.fixtures.system_id)['items'][0][
            'id']
        assert self.fixtures.ds_id is not None
        observation = {
            "datastream@id": self.fixtures.ds_id,
            "result": {
                "testboolean": False
            }
        }
        self.fixtures.observations_api.headers = {'Content-Type': 'application/om+json'}
        obs = self.fixtures.observations_api.observations_of_datastream(self.fixtures.ds_id)['items'][0]
        print(f'Original Obs: {obs}')
        res = self.fixtures.observations_api.observations_update(obs['id'], json.dumps(observation))
        obs = self.fixtures.observations_api.observations_of_datastream(self.fixtures.ds_id)['items'][0]
        print(f'Updated Obs: {obs}')
        assert obs['result']['testboolean'] is False

    def test_observations_delete(self):
        self.fixtures.ds_id = self.fixtures.datastream_api.datastreams_of_system(self.fixtures.system_id)['items'][0][
            'id']
        assert self.fixtures.ds_id is not None
        obs = self.fixtures.observations_api.observations_of_datastream(self.fixtures.ds_id)['items'][0]
        print(f'Original Obs: {obs}')
        res = self.fixtures.observations_api.observations_delete(obs['id'])
        obs = self.fixtures.observations_api.observations_of_datastream(self.fixtures.ds_id)
        print(f'Updated Obs: {obs}')
        assert obs['items'] == []


@pytest.mark.skip("Requires a subscription to the OSH server")
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


@pytest.mark.skip("Requires a subscription to a Control Stream that is beyond the current scope of the api")
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


@pytest.mark.skip("Requires stream on OSH server")
class TestSystemEvents:
    fixtures = OSHFixtures()
    system_event_def = {
        "resultTime": "2021-03-15T04:53:34Z",
        "result": 23.5
    }

    def test_system_events(self):
        print(self.fixtures)
        res = self.fixtures.system_events_api.system_events()
        print(res)
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
    fixtures = OSHFixtures()

    def test_system_history(self):
        res = self.fixtures.system_history_api.system_history('0s2lbn2n1bnc8')
        assert len(res['items']) > 0

    def test_system_history_by_id(self):
        res = self.fixtures.system_history_api.system_history_by_id('0s2lbn2n1bnc8', '2024-04-29T02:30:07.961Z')
        print(res)
        assert res['id'] == '0s2lbn2n1bnc8'

    @pytest.mark.xfail(
        reason="OSH only allows history events to in response to updates made directly to the system description")
    def test_system_history_update_description(self):
        updated_def = {
            "type": "Feature",
            "id": "0s2lbn2n1bnc8",
            "properties": {
                "uid": "urn:osh:sensor:simweathernetwork:001",
                "featureType": "http://www.w3.org/ns/sosa/Sensor",
                "name": "Simulated Weather Station Network",
                "description": "Updated description to include more data!!!",
            },
            "links": [
                {
                    "rel": "canonical",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8",
                    "type": "application/json"
                },
                {
                    "rel": "alternate",
                    "title": "Detailed description of system in SensorML format",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8",
                    "type": "application/sml+json"
                },
                {
                    "rel": "members",
                    "title": "List of subsystems",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8/members",
                    "type": "application/json"
                },
                {
                    "rel": "datastreams",
                    "title": "List of system datastreams",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8/datastreams",
                    "type": "application/json"
                },
                {
                    "rel": "controls",
                    "title": "List of system control channels",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8/controls",
                    "type": "application/json"
                },
                {
                    "rel": "samplingFeatures",
                    "title": "List of system features of interest",
                    "href": "http://localhost:8585/sensorhub/api/systems/0s2lbn2n1bnc8/featuresOfInterest",
                    "type": "application/json"
                }
            ]
        }
        res = self.fixtures.system_history_api.system_history_update_description('0s2lbn2n1bnc8',
                                                                                 '2024-04-29T02:30:07.961Z',
                                                                                 json.dumps(updated_def))
        print(res)
        assert res is not None

    @pytest.mark.skip(reason="Will break test server")
    def test_system_history_delete(self):
        assert False


def delete_all_systems():
    # delete datastreams first
    delete_all_datastreams()
    systems = OSHFixtures.systems_api.systems()
    for system in systems['items']:
        OSHFixtures.systems_api.system_delete(system['id'])


def delete_all_datastreams():
    datastreams = OSHFixtures.datastream_api.datastreams()
    for ds in datastreams['items']:
        OSHFixtures.datastream_api.datastream_delete(ds['id'])
