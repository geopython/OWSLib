Logging
=======

OWSLib logs messages to the 'owslib' named python logger.  You may configure your
application to use the log messages like so:

.. code-block:: python

    import logging
    owslib_log = logging.getLogger('owslib')
    # Add formatting and handlers as needed
    owslib_log.setLevel(logging.DEBUG)
