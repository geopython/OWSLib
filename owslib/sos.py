# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2013 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

"""
Sensor Observation Service (SOS) methods and metadata. Factory function.
"""

from __future__ import (absolute_import, division, print_function)

from .swe.observation import sos100, sos200
from .util import clean_ows_url


def SensorObservationService(url,
                             version='1.0.0',
                             xml=None,
                             username=None,
                             password=None,):
    """
    SOS factory function
    :param url: url of capabilities document
    :param version: SOS version 1.0.0 or 2.0.0
    :param xml: elementtree object
    :param username: username allowed to handle with SOS
    :param password: password for the username
    :return: a version specific SensorObservationService object
    """

    clean_url = clean_ows_url(url)

    if version in ['1.0', '1.0.0']:
        return sos100.SensorObservationService_1_0_0.__new__(
            sos100.SensorObservationService_1_0_0, clean_url, version,
            xml, username, password)
    elif version in ['2.0', '2.0.0']:
        return sos200.SensorObservationService_2_0_0.__new__(
            sos200.SensorObservationService_2_0_0, clean_url, version,
            xml, username, password)
