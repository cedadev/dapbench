"""
sub-package for jython-specific code.

"""
import sys

if 'java' not in sys.platform:
    raise ImportError("Module %s requires jython environment" % __name__)
