# -*- coding: UTF-8 -*-
from owslib.sos import SensorObservationService

from tests.utils import service_ok

import pytest

SERVICE_URL = 'http://sos.irceline.be/sos'


@pytest.mark.online
@pytest.mark.skipif(not service_ok(SERVICE_URL),
                    reason="SOS service is unreachable")
def test_sos_caps():
    sos = SensorObservationService(SERVICE_URL)
    assert str(sos.contents['81102 - PM10']) == "Offering id: 81102 - PM10, name: Particulate Matter < 10 µm"
    assert repr(sos.contents['81102 - PM10']) == "<SosObservationOffering 'Particulate Matter < 10 µm'>"
