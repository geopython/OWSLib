Development
===========

The OWSLib wiki is located at https://github.com/geopython/OWSLib/wiki

The OWSLib source code is available at https://github.com/geopython/OWSLib

You can find out about software metrics at the OWSLib OpenHub page at https://www.openhub.net/p/OWSLib.

Testing
-------

.. code-block:: bash

   $ python setup.py test

Or ...

.. code-block:: bash

    # install requirements
    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt # needed for tests only

    # run tests
    python -m pytest

    # additional pep8 tests
    pep8 owslib/wmts.py
