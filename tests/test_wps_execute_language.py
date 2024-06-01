import logging
import owslib.wps


def test_wps_execute_language(monkeypatch):

    def raise_on_log_error(*a):
        """Make sure the errors are raised, not only caught and logged"""
        raise AssertionError

    monkeypatch.setattr(logging, "error", raise_on_log_error)

    monkeypatch.setattr(owslib.wps.WPSExecution, "parseResponse", lambda *a: None)
    wps = owslib.wps.WebProcessingService('http://www.example.com', language='fr-CA', skip_caps=True)
    execution = wps.execute('test', [], response=b'<xml></xml>')

    assert b'language="fr-CA"' in execution.request

    def mock_open_url(*args, **kwargs):
        assert 'language=fr-CA' in args[1]

        class FakeResponse:
            def read(self):
                return b'<xml></xml>'

        return FakeResponse()

    monkeypatch.setattr(owslib.wps, "openURL", mock_open_url)

    execution.status = 'ProcessSucceeded'
    execution.checkStatus(url='http://www.example.com', response=None, sleepSecs=0)
