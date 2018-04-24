# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
initial test setup for Ows Context
"""

from __future__ import (absolute_import, division, print_function)

from tests.utils import resource_file, setup_logging
from tests.utils import scratch_file

from owslib.owscontext import core, common, geojson
from datetime import datetime

logger = setup_logging(loglevel='DEBUG')

def setup_module(module):
    """Setup for the owc test module"""
    logger.info('Inside Setup')
    # Do actual setup stuff here if necessary
    pass

def test_load_parse():
    jsondata = open(resource_file('owc1.geojson'), 'rb').read().decode('utf-8')
    # logger.debug(jsondata)
    my_dict = geojson.decode_json(jsondata)
    # logger.debug(str(my_dict))
    assert my_dict is not None


def test_encode_json():
    owc1 = core.OwcContext(id="http://ows.com/id1",
                           update_date=datetime.now(),
                           title="my context collection 1")
    red = geojson.skip_nulls(owc1.to_dict())
    logger.debug(red)

    assert owc1.id == "http://ows.com/id1"
    assert owc1.language == "en"
    assert owc1.title == "my context collection 1"
    assert len(owc1.keywords) == 0

    jsdata = owc1.to_json()
    logger.debug(jsdata)
    assert len(jsdata) > 0