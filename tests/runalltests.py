# $Id: runalltests.py,v 1.1.1.1 2004/12/06 03:28:23 sgillies Exp $

# =============================================================================
# Cartographic Objects for Zope. Copyright (C) 2004 Sean C. Gillies
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
# Contact email: sgillies@frii.com
# =============================================================================

import os, sys
import unittest

verbosity = 1
try:
    opts, args = getopt.getopt(sys.argv[1:], 'v')
    if opts[0][0] == '-v':
        verbosity = verbosity + 1
except:
    pass

runner = unittest.TextTestRunner(verbosity=verbosity)
suite = unittest.TestSuite()
load = unittest.defaultTestLoader.loadTestsFromModule

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test in tests:
    m = __import__(test)
    suite.addTest(load(m))

# =============================================================================
# Run
if __name__ == '__main__':
    runner.run(suite)

