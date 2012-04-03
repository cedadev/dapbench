# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
sub-package for jython-specific code.

"""
import sys

if 'java' not in sys.platform:
    raise ImportError("Module %s requires jython environment" % __name__)
