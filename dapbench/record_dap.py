#!/usr/bin/env python
"""
Execute a programme that makes NetCDF-API OPeNDAP calls capturing
request events and timings.

"""

import tempfile
import os, sys
from subprocess import Popen, PIPE
import re
import urllib

from curllog import DapRequest, DapStats

TMP_PREFIX='record_dap-'
DODSRC = '.dodsrc'
LOGFILE = 'record_dap.log'

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
        #!TODO: not suitable for secured opendap yet.
        fh = open(self.dodsrc)
        fh.write("""
DEFLATE=0
CURL.VERBOSE=1
""")

    def call(self, command):
        cmd = 'strace -ttt -f -e trace=network %s' % command
        pipe = Popen(cmd, shell=True, stderr=PIPE, 
                     stdout=open('/dev/null')).stderr

        return DapStats(self.iter_requests(pipe))

    def iter_requests(self, pipe):
        timestamp = None
        host = 'unknown'
        for line in pipe:
            mo = re.match('\* Connected to ([^\s]+)', line)
            if mo:
                host = mo.group(1)
            elif re.match('> GET ', line):
                #!TODO: handle other stderr output from wrapped tool
                req = urllib.unquote(line.strip()[2:])
                request = DapRequest.from_get(host, req)
                assert timestamp is not None
                yield (timestamp, request)
                timestamp = None
            else:                
                mo = re.match('(\d+\.\d+)\s+(send|recv)', line)
                if mo:
                    timestamp, syscall = mo.groups()
                    timestamp = float(timestamp)

        # Mark terminal event
        yield (timestamp, None)


if __name__ == '__main__':
    #test_dataset = 'http://esg-dev1.badc.rl.ac.uk:8081/ta_20101129/ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197812010600-197901010000.nc'
    w = Wrapper('.')
    stats = w.call('cdo runmean,20 http://esg-dev1.badc.rl.ac.uk:8080/opendap/ta_20101129/ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197812010600-197901010000.nc out.nc')
    ds_stats = stats.get_cursor()

    print ds_stats


