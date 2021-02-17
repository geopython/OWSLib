#!/usr/bin/env python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
#
# Authors : Francis Charette-Migneault (@fmigneault)
#
# =============================================================================

import json
import sys
import getopt
import os
import yaml

from owslib.ogcapi.processes import Processes


def usage():
    print("""
    
Usage: %s [parameters]

Common Parameters for all request types
-------------------

    -u, --url=[URL] the base URL of the WPS - required
    -r, --request=[REQUEST] the request type (GetCapabilities, DescribeProcess, Execute) - required 
    -v, --verbose set flag for verbose output - optional (defaults to False)    
    -o, --output=[FORMAT] format of the response to provide - optional {json, yaml}

Request Specific Parameters
---------------------------

    DescribeProcess
        -i, --identifier=[ID] process identifier - required
    Execute
        -d, --data, --json JSON file containing pre-made request to be submitted - required

Examples
--------
python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r GetCapabilities

python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r Processes

python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r DescribeProcess -i las2tif

python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r Execute -i las2tif -d payload.json
python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r Execute -i las2tif --json payload.json

python wps-rest-client.py -u https://ogc-ades.crim.ca/ADES -r GetStatus -j <JobId>

    with 'payload.json' contents: 
    
        {
          "mode": "async",
          "response": "document",
          "inputs": [
            {
              "id": "input",
              "href": "https://ogc-ems.crim.ca/wps-outputs/example-nc-array.json"
            }
          ],
          "outputs": [
            {
              "id": "output",
              "transmissionMode": "reference"
            }
          ]
        }

""" % sys.argv[0])


# check args
if len(sys.argv) == 1:
    usage()
    sys.exit(1)

print('ARGV      :', sys.argv[1:])

try:
    # json == data
    opts = ['url=', 'request=', 'json=', 'data=', 'identifier=', 'job=', 'output=', 'verbose']
    options, remainder = getopt.getopt(sys.argv[1:], 'u:r:d:i:j:o:v', opts)
except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)

print('OPTIONS   :', options)

url = None
request = None
identifier = None
job = None
data = None
verbose = False
output = None

for opt, arg in options:
    if opt in ('-u', '--url'):
        url = arg
    elif opt in ('-r', '--request'):
        request = arg
    elif opt in ('-d', '--data', '--json'):
        data = arg
    elif opt in ('-i', '--identifier'):
        identifier = arg
    elif opt in ('-j', '--job'):
        job = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-o', '--output'):
        output = arg
    else:
        assert False, 'Unhandled option'

# required arguments for all requests
if request is None or url is None:
    usage()
    sys.exit(3)


def print_content(output_format, output_content):
    if output_format == "yaml":
        print(yaml.safe_dump(output_content, indent=2, sort_keys=False, allow_unicode=True))
    elif output_format == "":
        print(json.dumps(output_content, indent=2, ensure_ascii=False))
    else:
        print(f"\nUnknown output format: {output_format}")
        sys.exit(20)


# instantiate client
wps = Processes(url)

if request == 'GetCapabilities':
    links = wps.links()
    if output:
        print_content(output, links)
        sys.exit(0)

    print('WPS Links:')
    for link in wps.links():
        print(f'  {link["title"]} ({link["rel"]})')
        print(f'  {link["href"]}')

elif request == 'Processes':
    processes = wps.processes()
    if output:
        print_content(output, processes)
        sys.exit(0)

    print('WPS Processes:')
    for process in processes:
        print(f'  identifier={process["id"]} title={process.get("title", "")}')

elif request == 'DescribeProcess':
    if identifier is None:
        print('\nERROR: missing mandatory "-i (or --identifier)" argument')
        usage()
        sys.exit(4)
    data = wps.process_description(identifier)
    if output:
        print_content(output, data)
        sys.exit(0)

    process = data["process"]
    print('WPS Process:')
    process.setdefault("abstract", "")
    print(f'  id={process["id"]}')
    for field in ["title", "version", "abstract"]:
        print(f'  {field}={process.get(field, "")}')
    print('  inputs:')
    for p_input in process["inputs"]:
        minOccurs = p_input.get("minOccurs", 1)
        maxOccurs = p_input.get("maxOccurs", 1)
        _domains = p_input.get("input", {}).get("literalDataDomain", {})
        _formats = p_input.get("formats", p_input.get("input", {}).get("format", []))  # FIXME: depending on impl
        print(f'  - id={p_input["id"]} title={p_input.get("title", "")} minOccurs={minOccurs} maxOccurs={maxOccurs}')
        if _formats:
            print(f'    formats:')
            for fmt in p_input["formats"]:
                _mime = fmt.get("mediaType", fmt.get("mimeType"))  # FIXME: depending on impl
                _default = " (default)" if fmt.get("default") else ""
                print(f'    - {_mime}{_default}')
        if "dataType" in _domains:
            print(f'    dataType={_domains["dataType"]}')
        # FIXME: support other variants (csr for bbox, literal value ranges, etc.)

    print('  outputs:')
    for p_output in process["outputs"]:
        _formats = p_output.get("formats", p_output.get("output", {}).get("format", []))  # FIXME: depending on impl
        print(f'  - id={p_output["id"]} title={p_output.get("title", "")}')
        if _formats:
            print(f'    formats:')
            for fmt in p_output["formats"]:
                print(f'    - {fmt}')

elif request == 'Execute':
    if identifier is None:
        print('\nERROR: missing mandatory "-i (or --identifier)" argument')
        usage()
        sys.exit(5)
    if data is None:
        print('\nERROR: missing mandatory "-d (or --data/--json)" argument')
        usage()
        sys.exit(6)
    data = os.path.abspath(data)
    if not os.path.isfile(data):
        print(f'\nERROR: File not found: {data}')
        sys.exit(7)
    with open(data, 'r') as f:
        payload = json.load(f)
    if not payload:
        print(f'\nERROR: Empty JSON data from {data}')
        sys.exit(7)

    status_location = wps.execute(identifier, payload)
    data, success = wps.monitor_execution(location=status_location)
    if output:
        print_content(output, data)
        sys.exit(0)

    print(f'Process execution: {data["status"]}')
    job = data["jobID"]
    path = f'{wps.url}/processes/{identifier}/jobs/{job}/results'
    if success:
        print(f'"Results location: {path}"')

elif request == 'GetStatus':
    if identifier is None:
        print('\nERROR: missing mandatory "-i (or --identifier)" argument')
        usage()
        sys.exit(8)
    if job is None:
        print('\nERROR: missing mandatory "-j (or --job)" argument')
        usage()
        sys.exit(9)

    data = wps.status(process_id=identifier, job_id=job)
    if output:
        print_content(output, data)
        sys.exit(0)

    print(f'Status: {data["status"]}')

else:
    print('\nERROR: Unknown request type')
    usage()
    sys.exit(6)
