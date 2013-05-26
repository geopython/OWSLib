Testing OWSLib
==============

The OWSLib module is tested with the help of setuptools

  http://peak.telecommunity.com/DevCenter/setuptools

Once you've used the ez_setup.py bootstrap module, use the tsetup.py script to
make a development build of cartography.data. I use /home/sean/egg-dev
as a staging area instead of the default (site-packages)

  $ python tsetup.py develop --install-dir=/home/sean/egg-dev

Next, copy runalltests.dist to runalltests and edit the PYTHONPATH to point to
your own staging area. Run it like

  $ ./runalltests

If you want just one test file

 $ python runalltests.py -t test_name.txt

Setuptools makes it a bit easier to guarantee we're testing the checked out
code, and not another installation of PCL.

Writing new tests
=================
Tests are written using doctest http://docs.python.org/library/doctest.html


