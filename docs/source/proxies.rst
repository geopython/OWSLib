Proxies Support
===============

OWSLib can be configured to work with proxy servers using environment variables.
These can either be set in a Python script (only affecting HTTP calls within that script), as in the example below:

.. code-block:: python

    import os
    from owslib.wms import WebMapService

    os.environ['HTTP_PROXY'] = 'http://10.10.1.10:3128'
    os.environ['HTTPS_PROXY'] = 'http://10.10.1.10:1080'
    wms = WebMapService('https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?', version='1.3.0')

Or through the operating system environment variables (Linux):

.. code-block:: bash

    $ export HTTP_PROXY="http://10.10.1.10:3128"
    $ export HTTPS_PROXY="http://10.10.1.10:1080"
    $ export ALL_PROXY="socks5://10.10.1.10:3434"

    $ python
    >>> from owslib.wms import WebMapService
    >>> wms = WebMapService('https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?', version='1.3.0')

Windows (PowerShell):

.. code-block:: ps1

    $env:HTTP_PROXY = "http://10.10.1.10:3128"
    $env:HTTPS_PROXY = "http://10.10.1.10:1080"
    $env:ALL_PROXY = "socks5://10.10.1.10:3434"

To use HTTP Basic Auth with your proxy, use the http://user:password@host/ syntax. For example:

.. code-block:: python

    os.environ['HTTP_PROXY'] = 'http://username:password@10.10.1.10:3128'


For more details, refer to the `Requests library documentation <https://requests.readthedocs.io/en/latest/user/advanced/#proxies>`__,
which OWSLib uses for all HTTP requests.
