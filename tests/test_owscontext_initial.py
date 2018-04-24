# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
initial test setup for Ows Context
"""

from tests.utils import resource_file
from tests.utils import scratch_file

from owslib.owscontext import core
from datetime import datetime
import pytest


def test_load_parse():
    jsondata = open(resource_file('owc1.geojson'), 'rb').read().decode('utf-8')
    # print(jsondata)
    my_dict = core.decode_json(jsondata)
    print(str(my_dict))
    assert my_dict is not None


def test_encode_json():
    owc1 = core.OwcContext(id="http://ows.com/id1",
                           update_date=datetime.now(),
                           title="my context collection 1")
    assert owc1.id == "http://ows.com/id1"
    assert owc1.language == "en"
    assert owc1.title == "my context collection 1"
    assert len(owc1.keywords) == 0
