# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================

from datetime import datetime
import json

import pytest

from owslib.ogcapi.connectedsystems import Commands, ControlChannels, Datastreams, Deployments, Observations, \
    Properties, SamplingFeatures, SystemEvents, SystemHistory, Systems
from owslib.util import Authentication


@pytest.fixture(scope="session")
def fixtures():
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

        def create_single_system(self):
            sys_api = Systems(self.TEST_URL, auth=self.auth, headers=self.sml_headers)
            sys_create_res = sys_api.system_create(json.dumps(self.system_definitions[0]))
            sys_id = sys_api.response_headers['Location'].split('/')[-1]
            return sys_id

        def create_single_datastream(self, system_id: str):
            ds_api = Datastreams(self.TEST_URL, auth=self.auth, headers=self.json_headers)
            result = ds_api.datastream_create_in_system(system_id, json.dumps(self.ds_definition))
            ds_id = ds_api.response_headers['Location'].split('/')[-1]
            return ds_id

        def delete_all_systems(self):
            # delete datastreams first
            self.delete_all_datastreams()
            self.delete_all_sampling_features()
            sys_api = Systems(self.TEST_URL, auth=self.auth, headers=self.sml_headers)
            systems = sys_api.systems()
            for system in systems['items']:
                self.systems_api.system_delete(system['id'])

        def delete_all_datastreams(self):
            datastreams = self.datastream_api.datastreams()
            for ds in datastreams['items']:
                self.datastream_api.datastream_delete(ds['id'])

        def delete_all_sampling_features(self):
            sampling_features = self.sampling_feature_api.sampling_features(use_fois=True)
            for sf in sampling_features['items']:
                self.sampling_feature_api.sampling_feature_delete(sf['id'], use_fois=True)

    yield OSHFixtures()


class TestSystems:
    @pytest.mark.online
    def test_system_readonly(self, fixtures):
        # get all systems
        res = fixtures.systems_api.systems()
        assert len(res['items']) > 0
        check_ids = ["0s2lbn2n1bnc8", "94n1f19ld7tlc"]
        assert [any(sys_id == item['id'] for item in res['items']) for sys_id in check_ids]

        # get a single system
        res = fixtures.systems_api.system(check_ids[0])
        assert res is not None
        assert res['id'] == check_ids[0]

    @pytest.mark.skip(reason="Skip transactional test")
    def test_system_functions(self, fixtures):
        # insertion of systems
        fixtures.systems_api.headers = fixtures.sml_headers
        sys_create_res = fixtures.systems_api.system_create(json.dumps(fixtures.system_definitions))
        assert sys_create_res is not None

        # update of system and retrieval
        sml_desc_copy = fixtures.sys_sml_to_update.copy()
        sml_desc_copy['description'] = 'Updated Description'
        sml_str = json.dumps(sml_desc_copy)
        post_systems = fixtures.systems_api.system_update('blid74chqmses', sml_str)

        check_result = fixtures.systems_api.system('blid74chqmses')
        assert check_result['properties']['description'] == 'Updated Description'

        # deletion of system
        all_systems = fixtures.systems_api.systems()

        # clear datastreams
        fixtures.delete_all_datastreams()

        for system in all_systems['items']:
            res = fixtures.systems_api.system_delete(system['id'])
            assert res == {}


class TestDeployments:
    @pytest.mark.skip(reason="Skip transactional test")
    def test_deployment_create(self, fixtures):
        res1 = fixtures.deployment_api.deployment_create(json.dumps(fixtures.deployment_definition))
        assert res1
        res2 = fixtures.deployment_api.deployments()
        assert fixtures.deployment_expected_id in [x['id'] for x in res2['items']]
        res3 = fixtures.deployment_api.deployment(fixtures.deployment_expected_id)
        assert res3['properties']['name'] == 'Test Deployment 001' and res3[
            'id'] == fixtures.deployment_expected_id

    @pytest.mark.skip(reason="Skip transactional test")
    def test_deployment_update(self, fixtures):
        fixtures.deployment_definition['properties']['description'] = 'Updated Description of Deployment 001'
        res = fixtures.deployment_api.deployment_update(fixtures.deployment_expected_id,
                                                             json.dumps(fixtures.deployment_definition))
        assert res is not None

    @pytest.mark.skip(reason="Skip transactional test")
    def test_deployment_delete(self, fixtures):
        res = fixtures.deployment_api.deployment_delete(fixtures.deployment_expected_id)
        assert res is not None


class TestSamplingFeatures:
    @pytest.mark.online
    def test_sampling_features_readonly(self, fixtures):
        all_features = fixtures.sampling_feature_api.sampling_features(use_fois=True)
        assert len(all_features['items']) == 51

        feature_id = "c4nce3peo8hvc"
        feature = fixtures.sampling_feature_api.sampling_feature(feature_id, use_fois=True)
        assert feature['id'] == feature_id
        assert feature['properties']['name'] == 'Station WS013'

    @pytest.mark.skip(reason="Skip transactional test")
    def test_sampling_features_all(self, fixtures):
        # setup
        fixtures.delete_all_systems()
        system_id = fixtures.create_single_system()

        # create a sampling feature
        fixtures.sampling_feature_api.headers = fixtures.geojson_headers
        res = fixtures.sampling_feature_api.sampling_feature_create(system_id,
                                                                         json.dumps(fixtures.feature_def), True)
        assert fixtures.sampling_feature_api.response_headers['Location'] is not None
        sampling_feature_id = fixtures.sampling_feature_api.response_headers['Location'].split('/')[-1]

        # get all sampling features
        res = fixtures.sampling_feature_api.sampling_features(use_fois=True)
        assert len(res['items']) > 0
        assert any(x['id'] == sampling_feature_id for x in res['items'])

        # get the sampling feature we created
        res = fixtures.sampling_feature_api.sampling_feature(sampling_feature_id, use_fois=True)
        assert res['properties']['name'] == 'Test Station 001'
        assert res['properties']['featureType'] == 'http://www.w3.org/ns/sosa/Station'

        # get sampling features from a system
        res = fixtures.sampling_feature_api.sampling_features_from_system(system_id, use_fois=True)
        assert len(res['items']) > 0
        assert any(x['id'] == sampling_feature_id for x in res['items'])

        # delete the sampling feature
        res = fixtures.sampling_feature_api.sampling_feature_delete(sampling_feature_id, use_fois=True)
        res = fixtures.sampling_feature_api.sampling_features(use_fois=True)
        assert res == {'items': []}


class TestDatastreams:
    @pytest.mark.online
    def test_datastreams_readonly(self, fixtures):
        ds_id = 'kjg2qrcm40rfk'
        datastreams = fixtures.datastream_api.datastreams()
        assert len(datastreams['items']) > 0
        assert any(x['id'] == ds_id for x in datastreams['items'])

        datastream = fixtures.datastream_api.datastream(ds_id)
        assert datastream['id'] == ds_id
        assert datastream['name'] == "Simulated Weather Station Network - weather"

    @pytest.mark.skip(reason="Skip transactional test")
    def test_all_ds_functions(self, fixtures):
        # preflight cleanup
        fixtures.delete_all_systems()
        # setup systems needed
        fixtures.systems_api.headers = fixtures.sml_headers
        # systems = fixtures.systems_api.system_create(json.dumps(fixtures.system_definitions))
        system = fixtures.create_single_system()

        # insert a datastream
        ds_def_str = json.dumps(fixtures.ds_definition)
        ds_api = Datastreams(fixtures.TEST_URL, auth=fixtures.auth, headers=fixtures.json_headers)
        datastream_create = ds_api.datastream_create_in_system(system, ds_def_str)

        # get the datastream id from Location header
        ds_id = ds_api.response_headers['Location'].split('/')[-1]
        ds = ds_api.datastream(ds_id)
        ds2 = ds_api.datastreams_of_system(system)
        assert ds['id'] == ds_id
        assert any(x['id'] == ds_id for x in ds2['items'])

        # update the datastream omitted due to server error
        # update schema has a similar server side issue

        # retrieve the schema for the datastream
        res = ds_api.datastream_retrieve_schema_for_format(ds_id)
        assert res is not None and len(res) > 0

        # delete the datastream
        ds_delete = ds_api.datastream_delete(ds_id)
        assert ds_delete == {}


class TestObservations:
    @pytest.mark.online
    def test_observations_readonly(self, fixtures):
        ds_id = 'kjg2qrcm40rfk'
        observations = fixtures.observations_api.observations_of_datastream(ds_id)
        assert len(observations['items']) > 0
        assert 'result' in observations['items'][0]

        observation_of_ds = fixtures.observations_api.observations_of_datastream(ds_id)
        assert observation_of_ds['items'][0]['result']['stationID'] == "WS013"
        keys = ['stationID', 'temperature', 'pressure', 'humidity', 'windSpeed', 'windDirection']
        assert [key in observation_of_ds['items'][0]['result'] for key in keys]

    @pytest.mark.skip(reason="Skip transactional test")
    def test_observations(self, fixtures):
        # setup
        fixtures.delete_all_systems()
        system = fixtures.create_single_system()
        ds = fixtures.create_single_datastream(system)
        the_time = datetime.utcnow().isoformat() + 'Z'

        observation = {
            "phenomenonTime": the_time,
            "resultTime": the_time,
            "result": {
                "timestamp": datetime.now().timestamp() * 1000,
                "testboolean": True
            }
        }
        fixtures.observations_api.headers = {'Content-Type': 'application/om+json'}
        res = fixtures.observations_api.observations_create_in_datastream(ds, json.dumps(observation))
        obs = fixtures.observations_api.observations_of_datastream(ds)
        assert obs['items'][0]['phenomenonTime'] == the_time
        obs_id = obs['items'][0]['id']
        res = fixtures.observations_api.observations_delete(obs_id)
        obs = fixtures.observations_api.observations_of_datastream(ds)
        assert obs['items'] == []
        fixtures.delete_all_systems()


class TestSystemHistory:
    @pytest.mark.online
    def test_system_history(self, fixtures):
        sys_id = '0s2lbn2n1bnc8'
        res = fixtures.system_history_api.system_history(sys_id)
        assert len(res['items']) > 0
        history_id = res['items'][0]['properties']['validTime'][0]
        res = fixtures.system_history_api.system_history_by_id(system_id=sys_id, history_id=history_id)
        assert res['id'] == sys_id
