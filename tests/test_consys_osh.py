# ==============================================================================
#  Copyright (c) 2024 Ian Patterson
#
#  Author: Ian Patterson <ian@botts-inc.com>
#
#  Contact email: ian@botts-inc.com
# ==============================================================================
import json

import pytest
import requests

from owslib.ogcapi.connectedsystems import Systems
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


@pytest.mark.online
# @pytest.mark.skipif(not service_ok(NODE_TEST_OK_URL), reason="service is unreachable")
def test_csapi_systems_osh():
    # systems_api = Systems(TEST_URL)
    systems_api = Systems(TEST_URL, auth=auth, headers={'Content-Type': 'application/json'})

    # Retrieve Systems
    # list_systems = systems_api.systems()
    # print(list_systems)
    list_systems = systems_api.systems()
    print(list_systems)

    list_systems_q = systems_api.systems(id='94n1f19ld7tlc')
    print(list_systems_q)
    list_systems_q = systems_api.systems(uid='urn:osh:sensor:simweathernetwork:001')
    print(list_systems_q)
    list_systems_q = systems_api.systems(foi=' urn:osh:sensor:simweather:station:WS001')
    print(list_systems_q)

    list_sys_by_id = systems_api.system('94n1f19ld7tlc')
    print(list_sys_by_id)

    # System Creation Examples
    print('\n')
    sys_json_strs = json.dumps(system_definitions)
    print(sys_json_strs)
    post_systems = systems_api.system_create(sys_json_strs)
    print(post_systems)

    systems_api.headers = {'Content-Type': 'application/sml+json'}
    sml_str = json.dumps(sys_sml_def)
    print(sml_str)
    post_systems = systems_api.system_create(sml_str)
    print(f'Response: {post_systems}')
    # systems_api.headers = {'Content-Type': 'application/json'}

    # System Update Examples
    sml_desc_copy = sys_sml_def.copy()
    sml_desc_copy['description'] = 'Updated Description'
    sml_str = json.dumps(sml_desc_copy)
    print(sml_str)
    systems_api.headers = {'Content-Type': 'application/sml+json'}
    post_systems = systems_api.system_update('blid74chqmses', sml_str)

    # System Delete
    # systems_api.system_delete('blid74chqmses')

    # System Components (Cannot Test with OSH yet)
    # systems_api.system_components_create('blid74chqmses', json.dumps(sml_component))

    # System Collection Retrival, addition, and deletion
    sys_collection = systems_api.collection('all_systems')
    print(sys_collection)
    sys_collection = systems_api.collection_item_create('all_systems', '0s2lbn2n1bnc8')
    print(sys_collection)


def test_csapi_procedures_osh():
    systems_api = Systems(TEST_URL, auth=auth, headers=sml_headers)



def raw_request():
    resp = requests.get(TEST_URL + 'systems', auth=('admin', 'admin'))
    print(resp.json())
