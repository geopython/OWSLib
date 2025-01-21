import json
import pytest

from owslib.ogcapi.coverages import Coverages


class MockCoverages(Coverages):
    def __init__(self, *args, **kwargs):
        kwargs["json_"] = '{}'  # avoid init API request
        super(MockCoverages, self).__init__(*args, **kwargs)

    def _request(self, **kwargs):
        json_args = json.dumps(kwargs)
        return json_args.encode("utf-8")


@pytest.mark.parametrize(
    ["kwargs", "expect"],
    [
        (
            {"unknown": "dropped-param"},
            {}
        ),
        (
            {"properties": ["B04"]},
            {"properties": "B04"},
        ),
        (
            {"properties": ["B04", "B08"]},
            {"properties": "B04,B08"},
        ),
        (
            {"scale_axes": [("Lat", 1), ("Lon", 2)]},
            {"scale-axes": "Lat(1),Lon(2)"},
        ),
        (
            {"scale_axes": (("Lat", 1), ("Lon", 2))},
            {"scale-axes": "Lat(1),Lon(2)"},
        ),
        (
            {"scale_axes": [["Lat", 1], ["Lon", 2]]},
            {"scale-axes": "Lat(1),Lon(2)"},
        ),
        (
            {"scale_axes": {"Lat": 1, "Lon": 2}},
            {"scale-axes": "Lat(1),Lon(2)"},
        ),
        (
            {"scale_size": [("Lat", 100), ("Lon", 200)]},
            {"scale-size": "Lat(100),Lon(200)"},
        ),
        (
            {"scale_size": (("Lat", 100), ("Lon", 200))},
            {"scale-size": "Lat(100),Lon(200)"},
        ),
        (
            {"scale_size": [["Lat", 100], ["Lon", 200]]},
            {"scale-size": "Lat(100),Lon(200)"},
        ),
        (
            {"scale_size": {"Lat": 100, "Lon": 200}},
            {"scale-size": "Lat(100),Lon(200)"},
        ),
        (
            {"scale_factor": 1.23},
            {"scale-factor": 1.23},
        ),
        (
            {"scale_factor": 2},
            {"scale-factor": 2},
        ),
        (
            {"scale_factor": 0.5},
            {"scale-factor": 0.5},
        ),
        (
            {"subset": {"Lat": [10, 20], "Lon": [30, 40]}},
            {"subset": "Lat(10:20),Lon(30:40)"},
        ),
        (
            {"subset": {"Lat": (10, 20), "Lon": (30, 40)}},
            {"subset": "Lat(10:20),Lon(30:40)"},
        ),
        (
            {"subset": [("Lat", 10, 20), ("Lon", 30, 40)]},
            {"subset": "Lat(10:20),Lon(30:40)"},
        ),
        (
            {"subset": [["Lat", 10, 20], ["Lon", 30, 40]]},
            {"subset": "Lat(10:20),Lon(30:40)"},
        ),
        (
            {"datetime": ("2025-01-01", "2025-01-02")},
            {"datetime": "2025-01-01/2025-01-02"},
        ),
        (
            {"datetime": ["2025-01-01", "2025-01-02"]},
            {"datetime": "2025-01-01/2025-01-02"},
        ),
        (
            {"datetime": "2025-01-01/2025-01-02"},
            {"datetime": "2025-01-01/2025-01-02"},
        ),
    ]
)
def test_coverages_coverage_kwargs(kwargs, expect):
    """
    Validate that additional keywords for coverages are parsed as intended.
    """
    cov = MockCoverages("")
    result = cov.coverage("test", **kwargs)
    args = result.read()
    params = json.loads(args)
    assert params["kwargs"] == expect
