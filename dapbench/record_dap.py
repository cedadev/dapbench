#!/usr/bin/env python
# BSD Licence
# Copyright (c) 2011, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.
"""
Execute a programme that makes NetCDF-API OPeNDAP calls, capturing
request events and timings.

This script uses 2 methods of capturing OPeNDAP requests:
 1. It assumes CURL.VERBOSE=1 in ~/.dodsrc
 2. It runns the command through "strace" to capture request timings

The result is a dapbench.dap_stats.DapStats object containing all OPeNDAP
requests made.

WARNING: It is possible to fool record_dap if the wrapped script
         writes to stderr lines begining "* Connected to" or "> GET"

"""

import tempfile
import os, sys
from subprocess import Popen, PIPE
import re
import urllib

from dapbench.dap_request import DapRequest
from dapbench.dap_stats import DapStats, SingleTimestampRecorder, echofilter_to_stats

import logging
log = logging.getLogger(__name__)

TMP_PREFIX='record_dap-'
DODSRC = '.dodsrc'

class Wrapper(object):
    def __init__(self, tmpdir=None):
        if tmpdir is None:
            tmpdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        self.tmpdir = tmpdir


    def check_dodsrc(self):
        try:
            rcpath = os.path.join(os.environ['HOME'], DODSRC)
            assert os.path.exists(rcpath)
            rcdata = open(rcpath).read()
            mo = re.search(r'^\s*CURL.VERBOSE\s*=\s*1', rcdata, re.M)
            assert mo
            log.debug('CURL.VERBOSE=1 confirmed')
        except AssertionError:
            raise Exception("~/.dodsrc doesn't have CURL.VERBOSE defined")

    def call(self, command):
        self.check_dodsrc()
        
        os.chdir(self.tmpdir)
        cmd = 'strace -ttt -f -e trace=network %s' % command
        log.info('Executing traced command: %s' % command)
        log.debug('Full command: %s' % cmd)
        pipe = Popen(cmd, shell=True, stderr=PIPE).stderr

        recorder = SingleTimestampRecorder(self.iter_requests(pipe))
        return recorder.stats

    def iter_requests(self, pipe):
        timestamp = None
        host = 'unknown'
        for line in pipe:
            mo = re.match('\* Connected to ([^\s]+)', line)
            if mo:
                host = mo.group(1)
                log.info('New Connection: %s' % host)
            elif re.match('> GET ', line):
                #!TODO: handle other stderr output from wrapped tool
                req = urllib.unquote(line.strip()[2:])
                request = DapRequest.from_get(host, req)
                log.info('Request: %s %s' % (timestamp, request))
                assert timestamp is not None
                yield (timestamp, request)
                timestamp = None
            else:                
                mo = re.match('(?:\[pid\s*(\d+)\])?\s*(\d+\.\d+)\s+(send|recv)', line)
                if mo:
                    pid, timestamp, syscall = mo.groups()
                    timestamp = float(timestamp)
                    #!TODO: track pids

        # Mark terminal event
        log.info('End: %s' % timestamp)
        yield (timestamp, None)


def make_parser():
    import optparse
    
    usage = "%prog [options] [--] command"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-s', '--stats', action="store", 
                      help="Store stats in the pickle file STATS")
    parser.add_option('-d', '--dir', action='store',
                      default='.',
                      help="Execute in directory DIR")
    parser.add_option('-l', '--loglevel', action='store',
                      default='INFO',
                      help="Set logging level")

    parser.add_option('-p', '--proxy', action="store",
                      help="Record via grinder TCPProxy output file.  Command is ignored")

    return parser

def record_curl(opts, args):
    if not args:
        parser.error("No command specified")
    
    w = Wrapper(opts.dir)
    command = ' '.join(args)
    stats = w.call(command)

    return stats

def record_proxy(opts, args):
    echofile = open(opts.proxy)
    return echofilter_to_stats(echofile)

def main(argv=sys.argv):
    import pickle

    parser = make_parser()
    
    opts, args = parser.parse_args()

    loglevel = getattr(logging, opts.loglevel)
    logging.basicConfig(level=loglevel)
    
    if opts.proxy:
        stats = record_proxy(opts, args)
    else:
        stats = record_curl(opts, args)

    stats.print_summary()

    if opts.stats:
        statfile = open(opts.stats, 'w')
        pickle.dump(stats, statfile)
        statfile.close()

if __name__ == '__main__':
    main()

