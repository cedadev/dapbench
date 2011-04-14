# BSD Licence
# Copyright (c) 2011, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Statistics on dap requests
"""

import numpy
import sys
import re

from dapbench.dap_request import DapRequest

class DapStats(object):
    """
    Container for OPeNDAP request statistics.
    """

    def __init__(self):
        self.datasets = {}

    def get_cursor(self, dataset=None):
        if dataset is None:
            dataset = self.datasets.keys()[0]

        return DapStatsCursor(self, dataset)

    def add_request(self, dataset, start_timestamp, stop_timestamp, request):
        ds_stat = self.datasets.setdefault(dataset, [])
        ds_stat.append((start_timestamp, stop_timestamp, request))
        

    def print_summary(self, fh=sys.stdout):
        for ds in self.datasets:
            print '#'*78
            print '  %s' % ds
            print
            c = self.get_cursor(ds)

            print 'Resp.\tCount\tTMean\tSMean'
            print
            for resp in ['das', 'dds', 'dods']:
                count = c.response_count(resp)
                tmean = c.response_tmean(resp)
                smean = c.response_smean(resp)
                print '%s\t%d\t%f\t%f' % (resp, count, tmean, smean)
        print


class SingleTimestampRecorder(object):
    """
    Gather statistics from a stream of DapRequests objects with single timestamps.

    When recording using the curl+strace method we only have timestamps for the
    start of requests.  Therefore we need to infer the end of the request from
    subsequent events.  This method takes a stream of (timestamp, DapRequest)
    terminated by (timestamp, None) and creates a DapStats object in self.stats

    """

    def __init__(self, timed_requests=None):
        self.stats = DapStats()

        self.last_timestamp = None
        self.last_request = None
        self.final = False

        self.update(timed_requests)


    def add_req(self, timestamp, request):
        if self.final:
            raise ValueError("Request stream has been finalised")

        if self.last_timestamp:
            self._unstage_req(timestamp)

        # Stage the current request
        self.last_timestamp = timestamp
        self.last_request = request
            
    def update(self, timed_requests):
        for timestamp, request in timed_requests:
            # If request is None it is the end timestamp.
            if request is None:
                self.final_event(timestamp)
                self.final = True
            else:
                self.add_req(timestamp, request)

    def final_event(self, timestamp):
        # Add final request
        self._unstage_req(timestamp)

    def _unstage_req(self, timestamp):
        # Add the last request
        if self.last_request:
            self.stats.add_request(self.last_request.dataset,
                                   self.last_timestamp, timestamp,
                                   self.last_request)
            


class DapStatsCursor(object):
    """
    Points to a specific dataset in DapStats.

    """
    def __init__(self, stats, dataset):
        self.ds_stats = stats.datasets[dataset]

    def response_count(self, response):
        return len(list(self._iter_response(response)))

    def response_tmean(self, response):
        ts = [end - start for start, end, req 
              in self._iter_response(response)]
        return numpy.mean(ts)

    def response_smean(self, response):
        ss = [req.size() for start, end, req in self._iter_response(response)]
        return numpy.mean(ss)

    def response_hist(self, response, bins=10):
        ts = [end - start for start, end, req
              in self._iter_response(response)]
        return numpy.histogram(ts, bins=bins)

    def _iter_response(self, response):
        return (t for t in self.ds_stats
                if t[2].response == response)



def echofilter_to_stats(file_handle):
    """
    Read the output from the custom grinder TCPProxy filter
    TimestampedEchoFilter to produce a DapStats object.

    """
    #!FIXME: this doesn't work because the connection is only closed once.

    stats = DapStats()
    open_requests = {}
    request = {}

    for line in file_handle:
        mo = re.match('--- ((.*)->(.*)) (opened|closed) (\d+) --', line)
        if mo:
            connection_details, source, dest, event, timestamp = mo.groups()
            timestamp = int(timestamp)

            if event == 'opened':
                assert connection_details not in open_requests
                open_requests[connection_details] = timestamp
            elif event == 'closed':
                start_timestamp = open_requests[connection_details]

                host, port = dest.split(':')
                stats.add_request(host, start_timestamp, timestamp, 
                                  request[connection_details])
                del open_requests[connection_details]
                del request[connection_details]
            else:
                raise Exception("Shouldn't get here")
                                 
            continue

        mo = re.match('------ ((.*)->(.*)) (\d+) ------', line)
        if mo:
            connection_details, source, dest = mo.groups()
            continue

        mo = re.match('GET ', line)
        if mo:
            request[connection_details] = DapRequest.from_get(source, line)
            continue

    return stats
