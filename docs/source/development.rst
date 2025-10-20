Development
===========

The OWSLib wiki is located at https://github.com/geopython/OWSLib/wiki

The OWSLib source code is available at https://github.com/geopython/OWSLib

You can find out about software metrics at the OWSLib OpenHub page at https://www.openhub.net/p/OWSLib.

Testing
-------

.. code-block:: bash

    # install requirements
    pip3 install -r requirements.txt
    pip3 install -r requirements-dev.txt # needed for tests only

    # run tests
    python3 -m pytest

    # linting
    flake8 owslib/wmts.py
