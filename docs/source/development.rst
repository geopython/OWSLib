Development
===========

The OWSLib wiki is located at https://github.com/geopython/OWSLib/wiki

The OWSLib source code is available at https://github.com/geopython/OWSLib

You can find out about software metrics at the OWSLib OpenHub page at https://www.openhub.net/p/OWSLib.

Testing
-------

Create a virtual environment and install OWSLib with the development dependencies:

.. code-block:: bash

    python3 -m venv owslibenv
    source owslibenv/bin/activate

    git clone https://github.com/geopython/OWSLib.git
    cd OWSLib

    pip install -e ".[dev]"

Run the test suite:

.. code-block:: bash

    python3 -m pytest

Run linting:

.. code-block:: bash

    flake8 owslib/

Documentation
-------------

To build the documentation locally:

.. code-block:: bash

    pip install -e ".[docs]"
    cd docs && make html

Release
-------

To install the release tooling:

.. code-block:: bash

    pip install -e ".[release]"
