# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
from collections import namedtuple
from datetime import datetime, timezone, timedelta
import json

import pytest
from pytest_httpserver import HTTPServer

from owslib.ogcapi.connectedsystems import Commands, ControlStreams, Datastreams, Deployments, Observations, \
    Properties, SamplingFeatures, SystemEvents, SystemHistory, Systems
from owslib.util import Authentication


@pytest.fixture(scope="session")
def fixtures():
    class OSHFixtures:
        NODE_TEST_OK_URL = 'http://34.67.197.57:8585/sensorhub/test'
        # Directs to OSH hosted test server
        # TEST_URL = 'http://34.67.197.57:8585/sensorhub/api/'
        SERVER = 'localhost'
        SERVER_PORT = 8585
        SERVER_CSAPI_EP = '/sensorhub/api/'
        TEST_URL = f'http://{SERVER}:{SERVER_PORT}{SERVER_CSAPI_EP}'
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
        control_channels_api = ControlStreams(TEST_URL, auth=auth,
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


@pytest.fixture(scope="session")
def system_ids():
    yield ["0s2lbn2n1bnc8", "94n1f19ld7tlc"]


@pytest.fixture(scope="session")
def system_definitions(system_ids):
    yield {
        system_ids[0]: {
            "type": "SimpleProcess",
            "uniqueId": "urn:osh:sensor:testsmlsensor:001",
            "label": "Test SML Sensor",
            "description": "A Sensor created from an SML document",
            "definition": "http://www.w3.org/ns/ssn/Sensor"
        },
        system_ids[1]: {
            "type": "SimpleProcess",
            "uniqueId": "urn:osh:sensor:testsmlsensor:002",
            "label": "Test SML Sensor #2",
            "description": "A Sensor created from an SML document",
            "definition": "http://www.w3.org/ns/ssn/Sensor"
        }
    }


@pytest.fixture(scope="session")
def feature_id():
    yield "c4nce3peo8hvc"


@pytest.fixture(scope="session")
def feature_definition(system_ids):
    yield {
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
            "parentSystem@link": {"href": f"http://localhost:8585/sensorhub/api/systems/{system_ids[0]}"},
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


@pytest.fixture(scope="session")
def datastream_ids():
    yield ["datastream001", "datastream002"]


@pytest.fixture(scope="session")
def datastream_definitions(datastream_ids):
    yield {
        datastream_ids[0]: {
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
    }


@pytest.fixture(scope="session")
def observation_ids():
    yield ["obs0001", "obs0002"]


@pytest.fixture(scope="session")
def times(observation_ids):
    TimeInfo = namedtuple('TimeInfo', ["iso_time", "timestamp"])
    iso_time = datetime.now(timezone.utc).isoformat() + 'Z'
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    yield TimeInfo(iso_time, timestamp)


def offset_time(timestamp, offset_seconds):
    dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    offset_dt = dt + timedelta(seconds=offset_seconds)
    TimeInfo = namedtuple('TimeInfo', ["iso_time", "timestamp"])
    return TimeInfo(offset_dt.isoformat() + 'Z', int(offset_dt.timestamp() * 1000))


@pytest.fixture(scope="session")
def observations_definitions(observation_ids, times):
    offset_ti = offset_time(times.timestamp, 1)
    yield {
        observation_ids[0]: {
            "phenomenonTime": times.iso_time,
            "resultTime": times.iso_time,
            "result": {
                "timestamp": times.timestamp,
                "testboolean": True
            }
        },
        observation_ids[1]: {
            "phenomenonTime": offset_ti.iso_time,
            "resultTime": offset_ti.iso_time,
            "result": {
                "timestamp": offset_ti.timestamp,
                "testboolean": False
            }
        }
    }


@pytest.fixture(scope="session")
def controlstream_ids():
    # yield ["ctrlchan123", "ctrlchan456"]
    yield ["ctrlchan123"]


@pytest.fixture(scope="session")
def controlstream_definitions(controlstream_ids):
    yield {
        controlstream_ids[0]: {
            "name": "Test Control Channel 001",
            "description": "A test control channel",
            "issueTime": None,
            "executionTime": None,
            "live": False,
            "async": True,
            "schema": {
                "commandFormat": "application/json",
                "parametersSchema": {
                    "type": "DataRecord",
                    "fields": [
                        {
                            "type": "Text",
                            "name": "textCommand",
                            "definition": "http://test.com/Command",
                            "label": "Text Command"
                        }
                    ]
                }
            }
        }
    }


@pytest.fixture(scope="session")
def command_ids():
    yield ["cmd0001", "cmd0002"]


@pytest.fixture(scope="session")
def command_definitions(command_ids):
    yield {
        command_ids[0]: {
            "parameters": {
                "textCommand": "Start Measurement"
            }
        },
        command_ids[1]: {
            "parameters": {
                "textCommand": "Stop Measurement"
            }
        }
    }


@pytest.fixture(scope="session")
def server_data(system_definitions, system_ids, feature_id, feature_definition, datastream_ids, datastream_definitions,
                controlstream_definitions, observation_ids, observations_definitions, command_definitions):
    class ServerData:
        systems = {
            "items": list(system_definitions.values())
        }
        features = {
            "items": [
                feature_definition
            ]
        }
        datastreams = {
            "items": list(datastream_definitions.values())
        }
        controlstreams = {
            "items": list(controlstream_definitions.values())
        }
        observations = {
            "items": list(observations_definitions.values())
        }
        commands = {
            "items": list(command_definitions.values())
        }

    yield ServerData


@pytest.mark.online
def test_systems_get(server_data, system_ids, system_definitions):
    with HTTPServer(port=8585) as ts:
        # This is not strictly what a server would respond with, but sufficient for testing
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request('/sensorhub/api/systems').respond_with_json(
            (server_data.systems))
        ts.expect_request(f'/sensorhub/api/systems/{system_ids[0]}').respond_with_json(
            system_definitions[system_ids[0]])
        ts.expect_request('/sensorhub/api/systems/94n1f19ld7tlc').respond_with_json(
            system_definitions[system_ids[1]])
        ts.expect_request(f'/sensorhub/api/systems', method='POST').respond_with_json({}, status=201, headers={
            'Location': 'http://localhost:8585/sensorhub/api/systems/insertedsystem001'})

        systems_api = Systems('http://localhost:8585/sensorhub/api/', auth=None,
                              headers={'Content-Type': 'application/json'})

        # get all systems
        res = systems_api.systems()
        assert len(res['items']) == 2
        check_ids = system_ids
        assert res['items'] == server_data.systems['items']

        # get a single system
        res = systems_api.system(check_ids[0])
        assert res is not None
        assert res == system_definitions[check_ids[0]]


@pytest.mark.online
def test_datastreams_get(server_data, datastream_ids, datastream_definitions):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request('/sensorhub/api/datastreams').respond_with_json(
            server_data.datastreams)
        for ds_id in datastream_ids:
            ts.expect_request(f'/sensorhub/api/datastreams/{ds_id}').respond_with_json(
                datastream_definitions)

        datastream_api = Datastreams('http://localhost:8585/sensorhub/api/', auth=None,
                                     headers={'Content-Type': 'application/json'})

        # get all datastreams
        res = datastream_api.datastreams()
        ds_ret = res['items']
        assert len(ds_ret) == 1

        # get a single datastream
        for ds_id in datastream_ids:
            res = datastream_api.datastream(ds_id)
            assert res is not None
            assert res == datastream_definitions


@pytest.mark.online
def test_observations_get(server_data, observation_ids, observations_definitions):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request('/sensorhub/api/observations').respond_with_json(
            server_data.observations)
        for obs_id in observation_ids:
            ts.expect_request(f'/sensorhub/api/observations/{obs_id}').respond_with_json(
                observations_definitions[obs_id])

        observations_api = Observations('http://localhost:8585/sensorhub/api/', auth=None,
                                        headers={'Content-Type': 'application/json'})

        # get all observations
        res = observations_api.observations()
        obs_ret = res['items']
        assert len(obs_ret) == 2

        # get a single observation
        for obs_id in observation_ids:
            res = observations_api.observation(obs_id)
            assert res is not None
            assert res == observations_definitions[obs_id]


@pytest.mark.online
def test_controlstreams_get(server_data, controlstream_ids, controlstream_definitions):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request('/sensorhub/api/controlstreams').respond_with_json(
            server_data.controlstreams)
        for cs_id in controlstream_ids:
            ts.expect_request(f'/sensorhub/api/controlstreams/{cs_id}').respond_with_json(
                controlstream_definitions[cs_id])

        control_channels_api = ControlStreams('http://localhost:8585/sensorhub/api/', auth=None,
                                              headers={'Content-Type': 'application/json'})

        # get all control channels
        res = control_channels_api.controlstreams()
        cs_ret = res['items']
        assert len(cs_ret) == 1

        # get a single control channel
        res = control_channels_api.controlstream(controlstream_ids[0])
        assert res is not None
        assert res == controlstream_definitions.get(controlstream_ids[0])


@pytest.mark.online
def test_commands_get(server_data, command_ids, command_definitions):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request('/sensorhub/api/commands').respond_with_json(
            server_data.commands)
        for cmd_id in command_ids:
            ts.expect_request(f'/sensorhub/api/commands/{cmd_id}').respond_with_json(
                command_definitions[cmd_id])

        commands_api = Commands('http://localhost:8585/sensorhub/api/', auth=None,
                                headers={'Content-Type': 'application/json'})

        # get all commands
        res = commands_api.commands()
        cmd_ret = res['items']
        assert len(cmd_ret) == 2

        # get a single command
        for cmd_id in command_ids:
            res = commands_api.command(cmd_id)
            assert res is not None
            assert res == command_definitions[cmd_id]


#  Tests for resource creation don't work well against a mocked server since the design of the core OGC api request method does not make the headers available
@pytest.mark.online
def test_system_insert(server_data, system_definitions, system_ids):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        # ts.expect_request('/sensorhub/api/systems').respond_with_json(
        #     (server_data.systems))
        ts.expect_request(f'/sensorhub/api/systems', method='POST').respond_with_json({}, status=201, headers={
            'Location': f'http://localhost:8585/sensorhub/api/systems/{system_ids[0]}'})

        systems_api = Systems('http://localhost:8585/sensorhub/api/', auth=None,
                              headers={'Content-Type': 'application/json'})

        # insert a system
        res = systems_api.system_create(json.dumps(system_definitions.get(system_ids[0])))
        assert res == {}


@pytest.mark.online
def test_datastream_insert(server_data, datastream_definitions, datastream_ids, system_ids):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request(f'/sensorhub/api/systems/{system_ids[0]}/datastreams', method='POST').respond_with_json({},
                                                                                                                  status=201,
                                                                                                                  headers={
                                                                                                                      'Location': f'http://localhost:8585/sensorhub/api/datastreams/{datastream_ids[0]}'})

        datastream_api = Datastreams('http://localhost:8585/sensorhub/api/', auth=None,
                                     headers={'Content-Type': 'application/json'})

        # insert a datastream
        res = datastream_api.datastream_create_in_system(system_ids[0], json.dumps(
            datastream_definitions.get(datastream_ids[0])))
        assert res == {}


@pytest.mark.online
def test_observation_insert(server_data, observations_definitions, observation_ids, datastream_ids):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request(f'/sensorhub/api/datastreams/{datastream_ids[0]}/observations',
                          method='POST').respond_with_json({}, status=201, headers={
            'Location': f'http://localhost:8585/sensorhub/api/observations/{observation_ids[0]}'})

        observations_api = Observations('http://localhost:8585/sensorhub/api/', auth=None,
                                        headers={'Content-Type': 'application/json'})

        # insert an observation
        res = observations_api.observations_create_in_datastream(datastream_ids[0], json.dumps(
            observations_definitions.get(observation_ids[0])))
        assert res == {}


@pytest.mark.online
def test_controlstream_insert(server_data, controlstream_definitions, controlstream_ids, system_ids):
    with (HTTPServer(port=8585) as ts):
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request(f'/sensorhub/api/systems/{system_ids[0]}/controlstreams',
                          method='POST'
                          ).respond_with_json({},
                                              status=201,
                                              headers={
                                                  'Location': f'http://localhost:8585/sensorhub/api/controlstreams/{controlstream_ids[0]}'})

        control_channels_api = ControlStreams('http://localhost:8585/sensorhub/api/', auth=None,
                                              headers={'Content-Type': 'application/json'})

        # insert a control stream
        res = control_channels_api.control_create_in_system(system_ids[0], json.dumps(
            controlstream_definitions.get(controlstream_ids[0])))
        assert res == {}


@pytest.mark.online
def test_command_insert(server_data, command_definitions, command_ids, controlstream_ids):
    with HTTPServer(port=8585) as ts:
        ts.expect_request('/sensorhub/api/').respond_with_json({"title": "SensorHub OGC API - Connected Systems"})
        ts.expect_request(f'/sensorhub/api/controlstreams/{controlstream_ids[0]}/commands',
                          method='POST').respond_with_json({}, status=201, headers={
            'Location': f'http://localhost:8585/sensorhub/api/commands/{command_ids[0]}'})

        commands_api = Commands('http://localhost:8585/sensorhub/api/', auth=None,
                                headers={'Content-Type': 'application/json'})

        # insert a command
        res = commands_api.commands_send_command_in_control_stream(controlstream_ids[0], json.dumps(
            command_definitions.get(command_ids[0])))
        assert res == {}
