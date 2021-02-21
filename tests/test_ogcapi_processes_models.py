"""Use the examples from ogcapi-processes/core/examples/json/ to check data models.

Most of these fails because there are inconsistencies between the schemas, the examples and the live server
implementations.

Format :
 mediaType vs mimeType

LiteralDataType:
 literalDataDomain vs literalDataDomains

JobList:
  Example has id fields, with info...

TODO: Fetch the json files from github. Probably need caching to avoid hitting usage limits on github. A fixture?
TODO: For each json response, instantiate the corresponding class.
"""
import os
import pytest
import json
from pathlib import Path
import owslib.ogcapi.models as m

# Path to the ogcapi-processes/core/examples/json directory
PATH = os.environ.get("PATH_OGCAPI_PROCESSES_EXAMPLES")
PATH = Path(PATH) if PATH is not None else PATH


@pytest.mark.skipif(PATH is None, reason="No json examples")
class TestModels:

    def test_confclasses(self):
        fn = PATH / "ConfClasses.json"
        m.ConfClasses.parse_file(fn)

    @pytest.mark.xfail
    def test_execute(self):
        fn = PATH / "Execute.json"
        # m.Execute.parse_file(fn)
        obj = json.loads(fn.read_text())
        m.Execute.parse_obj(obj)

    @pytest.mark.xfail
    def test_input(self):
        fn = PATH / "Execute.json"
        obj = json.loads(fn.read_text())
        m.Input.parse_obj(obj["inputs"]["complexInputId"])
        m.Input.parse_obj(obj["inputs"]["complexInputsId"])
        m.Input.parse_obj(obj["inputs"]["literalInputId"])
        m.Input.parse_obj(obj["inputs"]["boundingboxInputId"])
        m.Input.parse_obj(obj["inputs"])

    @pytest.mark.xfail
    def test_joblist(self):
        fn = PATH / "JobList.json"
        m.JobList.parse_file(fn)

    def test_landingpage(self):
        fn = PATH / "LandingPage.json"
        m.LandingPage.parse_file(fn)

    @pytest.mark.xfail
    def test_processdescription(self):
        fn = PATH / "ProcessDescription.json"
        m.Process.parse_file(fn)

    def test_processlist(self):
        fn = PATH / "ProcessList.json"
        m.ProcessList.parse_file(fn)

    def test_result(self):
        fn = PATH / "Result.json"
        m.Result.parse_file(fn)

    def test_statusinfo(self):
        fn = PATH / "StatusInfo.json"
        m.StatusInfo.parse_file(fn)

    def test_statusinfo_dismissed(self):
        fn = PATH / "StatusInfo-dismissed.json"
        m.StatusInfo.parse_file(fn)
