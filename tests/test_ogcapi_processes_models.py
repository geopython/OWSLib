"""Use the examples from ogcapi-processes/core/examples/json/ to check data models.

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

    def test_input(self):
        fn = PATH / "Execute.json"
        obj = json.loads(fn.read_text())
        m.Input.parse_obj(obj["inputs"]["complexInputId"])
        m.Input.parse_obj(obj["inputs"]["complexInputsId"])
        m.Input.parse_obj(obj["inputs"]["literalInputId"])
        m.Input.parse_obj(obj["inputs"]["boundingboxInputId"])
        m.Input.parse_obj(obj["inputs"])

