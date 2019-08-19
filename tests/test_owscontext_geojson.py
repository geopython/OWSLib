# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
initial test setup for Ows Context
"""

# TODO make dates from (currently) string to datetime instances
from datetime import datetime

from owslib.owscontext.common import TimeIntervalFormat, skip_nulls, extract_p
from owslib.owscontext.core import OwcResource, OwcContext
from owslib.owscontext.geojson import decode_json
from tests.utils import resource_file, setup_logging

import os

logger = setup_logging(loglevel='INFO')

def setup_module(module):
    """Setup for the owc test module"""
    logger.debug('Setup logging in debug')
    # Do actual setup stuff here if necessary
    pass


def test_time_interval_format():
    single_date_str = "2013-11-02T15:24:24.446+12:00"
    interval_date_str = "2011-11-04T00:01:23Z/2017-12-05T17:28:56Z"
    bogus = "2011-11-04"

    ti1 = TimeIntervalFormat.from_string(single_date_str)
    assert isinstance(ti1.start, datetime)
    logger.debug(ti1.__str__())
    logger.debug(ti1.start.isoformat())

    ti2 = TimeIntervalFormat.from_string(interval_date_str)
    assert isinstance(ti2.start, datetime)
    assert isinstance(ti2.end, datetime)
    logger.debug(ti2.__str__())
    logger.debug(ti2.end.isoformat())

    ti3 = TimeIntervalFormat.from_string(bogus)
    assert isinstance(ti3.start, datetime)
    logger.debug(ti3.__str__())


def test_extract_p():
    t1 = {"date": "2013-11-02T15:24:24.446+12:00"}
    assert isinstance(t1, dict)
    assert t1.items() is not None
    assert t1.get('date') == "2013-11-02T15:24:24.446+12:00"
    t2 = extract_p('date', t1, None)
    assert t2 is not None
    assert t1.get('date') == t2


def test_json_decode():
    jsdata = """{
  "type": "FeatureCollection",
  "id": "http://www.opengis.net/owc/1.0/examples/wps_52north/",
  "features": [
    {
      "id": "http://geoprocessing.demo.52north.org:8080/wps/WebProcessingService/process1/",
      "geometry": null,
      "properties": {
        "categories": [],
        "date": "2013-11-02T15:24:24.446+12:00"
      }
    }
  ]
}"""
    result = decode_json(jsdata)
    assert result is not None
    assert result['features'][0]['properties']['date'] == "2013-11-02T15:24:24.446+12:00"


def test_decode_single_json():
    jsondata1 = open(resource_file(os.path.join('owc_geojson_examples', 'owc1.geojson')), 'r').read()

    result = decode_json(jsondata1)
    assert result is not None
    assert result['features'][0]['properties']['date'] == "2013-11-02T15:24:24.446+12:00"


def test_encode_json_small():
    feat = OwcResource(id="http://the.resource.com/id=1",
                            update_date=datetime.now(),
                            title="resource title",
                            temporal_extent=TimeIntervalFormat.from_string(
                                "2013-11-02T15:24:24.446+12:00"))
    assert feat.temporal_extent.to_dict() == TimeIntervalFormat.from_string(
        "2013-11-02T15:24:24.446+12:00").to_dict()

    t1 = feat.to_dict()
    t2 = skip_nulls(feat.to_dict())

    assert t1.get('temporal_extent') == t2.get('temporal_extent')

    owc1 = OwcContext(id="http://ows.com/id1",
                           update_date=datetime.now(),
                           title="my context collection 1",
                           time_interval_of_interest=TimeIntervalFormat.from_string(
                               "2013-11-02T15:24:24.446+12:00"),
                           resources=[])
    assert owc1.time_interval_of_interest.to_dict() == TimeIntervalFormat.from_string(
        "2013-11-02T15:24:24.446+12:00").to_dict()

    t3 = skip_nulls(owc1.to_dict())

    assert owc1.id == "http://ows.com/id1"
    assert owc1.language == "en"
    assert owc1.title == "my context collection 1"
    assert len(owc1.keywords) == 0

    jsdata = owc1.to_json()
    logger.debug(jsdata)
    assert len(jsdata) > 0


def test_decode_json_small():
    owc1 = OwcContext(id="http://ows.com/id1",
                           update_date=datetime.now(),
                           title="my context collection 1")
    jsdata = owc1.to_json()
    owc2 = OwcContext.from_json(jsdata)
    assert owc2 is not None
    assert isinstance(owc2, OwcContext)
    logger.debug(owc2.to_dict())
    assert owc2.id == "http://ows.com/id1"
    assert owc2.language == "en"
    assert owc2.title == "my context collection 1"
    assert len(owc1.keywords) == 0


def test_load_parse():
    jsondata = open(resource_file(os.path.join('owc_geojson_examples', 'owc1.geojson')), 'rb').read().decode('utf-8')
    # logger.debug(jsondata)
    my_dict = decode_json(jsondata)
    logger.debug(str(my_dict))
    assert my_dict is not None


def test_decode_full_json1():
    jsondata1 = open(resource_file(os.path.join('owc_geojson_examples', 'owc1.geojson')), 'r').read()
    owc1 = OwcContext.from_json(jsondata1)
    assert owc1 is not None
    assert owc1.resources[0].temporal_extent.to_dict() == TimeIntervalFormat.from_string(
        "2013-11-02T15:24:24.446+12:00").to_dict()
    # logger.debug(owc1.to_json())
    re_owc1 = OwcContext.from_json(owc1.to_json())
    assert owc1.to_dict() == re_owc1.to_dict()

    getcapa_ops = [op for op in owc1.resources[0].offerings[0].operations if op.operations_code == "GetCapabilities"]
    assert len(getcapa_ops) > 0
    assert getcapa_ops[0].mimetype == "application/xml"

def test_decode_full_json2():
    jsondata2 = open(resource_file(os.path.join('owc_geojson_examples', 'owc2.geojson')), 'rb').read().decode('latin1')
    owc2 = OwcContext.from_json(jsondata2)
    assert owc2 is not None
    # logger.debug(owc2.to_json())
    re_owc2 = OwcContext.from_json(owc2.to_json())
    assert owc2.to_dict() == re_owc2.to_dict()

    assert owc2.creator_application.title == "Web Enterprise Suite"
    assert owc2.spec_reference[0].href == "http://www.opengis.net/spec/owc-geojson/1.0/req/core"
    assert isinstance(owc2.resources[0].geospatial_extent, dict)
    geo = owc2.resources[0].geospatial_extent
    assert geo.get('type') == "Polygon"
    assert isinstance(geo.get('coordinates'), list)


def test_decode_full_json3():
    jsondata3 = open(resource_file(os.path.join('owc_geojson_examples', 'owc3.geojson')), 'rb').read().decode('utf-8')

    owc3 = OwcContext.from_json(jsondata3)
    assert owc3 is not None
    logger.debug(owc3.to_json())
    re_owc3 = OwcContext.from_json(owc3.to_json())
    assert owc3.to_dict() == re_owc3.to_dict()

    assert owc3.creator_display.pixel_width == 800
    assert owc3.authors[0].email == "a.kmoch@gns.cri.nz"

    assert len(owc3.keywords) == 5
    assert owc3.resources[0].keywords[0].label == "Informative Layers"

    links_via = [l for l in owc3.context_metadata if
                 l.href == "http://portal.smart-project.info/context/smart-sac.owc.json"]
    assert len(links_via) == 1

    assert owc3.resources[0].temporal_extent.to_dict() == TimeIntervalFormat.from_string(
        "2011-11-04T00:01:23Z/2017-12-05T17:28:56Z").to_dict()

    wms_offering = [of for of in owc3.resources[0].offerings if
                    of.offering_code == "http://www.opengis.net/spec/owc-geojson/1.0/req/wms"]
    assert len(wms_offering) > 0
    assert wms_offering[0].styles[
               0].legend_url == "http://docs.geoserver.org/latest/en/user/_images/line_simpleline1.png"


def test_load_bulk():
    js1 = open(resource_file(os.path.join('owc_geojson_examples','from-meta-resource.json')), 'r').read()
    js2 = open(resource_file(os.path.join('owc_geojson_examples','ingest1.owc.geojson')), 'r').read()
    js3 = open(resource_file(os.path.join('owc_geojson_examples','newzealand-overview.json')), 'r').read()
    js4 = open(resource_file(os.path.join('owc_geojson_examples','owc1.geojson')), 'r').read()
    js5 = open(resource_file(os.path.join('owc_geojson_examples','owc2.geojson')), 'r').read()
    js6 = open(resource_file(os.path.join('owc_geojson_examples','owc3.geojson')), 'r').read()
    js7 = open(resource_file(os.path.join('owc_geojson_examples','sac-casestudies.json')), 'r').read()

    feeds = [js1, js2, js3,js4, js5, js6, js7 ]

    for f in feeds:
        logger.debug(f)
        dict_obj = decode_json(f)
        assert dict_obj is not None
        # logger.debug(dict_obj)
        owc = OwcContext.from_dict(dict_obj)
        assert owc is not None
        # logger.debug(OwcContext.from_dict(dict_obj).to_json())
        jsdata = owc.to_json()
        assert jsdata is not None
        assert len(jsdata) > 10
        re_owc = OwcContext.from_json(jsdata)
        assert re_owc is not None
        through = OwcContext.from_json(f)
        assert owc.to_dict() == through.to_dict()



