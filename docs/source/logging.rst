Logging
=======

OWSLib logs messages to the 'owslib' named Python logger.  You may configure your
application to use the log messages as follows:

.. code-block:: python

    import logging

    owslib_logger = logging.getLogger('owslib')

    # Add formatting and handlers as needed
    owslib_logger.setLevel(logging.DEBUG)
