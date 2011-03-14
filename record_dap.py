#!/usr/bin/env python
"""
Execute a programme that makes NetCDF-API OPeNDAP calls capturing
request events and timings.

"""

import tempfile
import os, sys
from subprocess import Popen, PIPE
import re

TMP_PREFIX='record_dap-'
DODSRC = '.dodsrc'

class Wrapper(object):
    def __init__(self, tmpdir=None):
        if tmpdir is None:
            tmpdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        self.tmpdir = tmpdir
        self.dodsrc = os.path.join(self.tmpdir, DODSRC)
        self.logfile = os.path.join(self.tmpdir, LOGFILE)

    def config_environment(self):
        os.environ['HOME'] = self.tmpdir

    def write_dodsrc(self):
        fh = open(self.dodsrc)
        fh.write("""
DEFLATE=0
CURL.VERBOSE=1
""")

    def trace_exec(self, command):
        cmd = 'strace -ttt -f -e trace=network %s' % command
        pipe = Popen(cmd, shell=True, stdout=PIPE).stdout

        return self.filter_output(pipe)

    def filter_output(self, pipe):
        for line in pipe:
            if re.match('^> GET|[\d\:\.]+\ssend\(\d+, "GET'):
                yield line
