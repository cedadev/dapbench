#!/usr/bin/env python
"""
Process a curl verbose log to capture OpenDAP requests.

"""

import re
import sys
import urllib

import numpy

class DapRequest(object):
    def __init__(self, dataset, response, projection, subset):
        self.response = response
        self.dataset = dataset
        self.projection = projection
        self.subset = subset

    def __str__(self):
        return '<DapRequest %s %s %s>' % (self.response, self.projection, self.subset)

    def size(self):
        if not self.subset:
            return 0
        size = 1
        for sel in self.subset:
            if type(sel) == slice:
                size *= (sel.stop - sel.start)
        return size

    @classmethod
    def from_get(klass, host, get_request):
        mo = re.match(r'GET ([^?]*)\.([^?]+)(\?.*)? HTTP/[0-9.]+\s*$', get_request)
        if not mo:
            raise ValueError("GET request not recognised")
        path, response, query = mo.groups()
        
        if query:
            mo = re.match(r'\?([^\[]+)($|\[.*)', query)
            if not mo:
                raise ValueError("Query %s not recognised" % query)
            projection, subset_str = mo.groups()
            
            sel_seq = re.findall(r'\[(\d+):?(\d+)?\]', subset_str)
            subset = []
            for start, stop in sel_seq:
                if stop:
                    subset.append(slice(int(start), int(stop)))
                else:
                    subset.append(int(start))
        else:
            projection = None
            subset = None
                    
        dataset = 'http://%s%s' % (host, path)
        return klass(dataset, response, projection, subset)


class DapStats(object):
    """
    Gather statistics about a stream of DapRequests objects.

    """


    def __init__(self, timed_requests=None):
        self.datasets = {}

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

    def get_cursor(self, dataset=None):
        if dataset is None:
            dataset = self.datasets.keys()[0]

        return DapStatsCursor(self, dataset)

    def _unstage_req(self, timestamp):
        # Add the last request
        ds_stat = self.datasets.setdefault(self.last_request.dataset, [])
        ds_stat.append((self.last_timestamp, timestamp, self.last_request))



class DapStatsCursor(object):
    """
    Points to a specific dataset in DapStats.

    """
    def __init__(self, stats, dataset):
        self.ds_stats = stats.datasets[dataset]

    def response_count(self, response):
        return len(list(self._iter_response(response)))

    def response_tmean(self, response):
        ts = (end - start for start, end, req 
              in self._iter_response(response))
        return mean(ts)

    def response_hist(self, response, bins=10):
        ts = (end - start for start, end, req
              in self._iter_response(response))
        return numpy.histogram(ts, bins=bins)

    def _iter_response(self, response):
        return (t for t in self.ds_stats
                if t[2].response == response)


def iter_requests(fh):
    for line in fh:
        mo = re.match('\* Connected to ([^\s]+)', line)
        if mo:
            host = mo.group(1)
        elif re.match(r'> GET', line):
            req = urllib.unquote(line.strip()[2:])
            yield DapRequest.from_get(host, req)

if __name__ == '__main__':
    logfile, = sys.argv[1:]

    for request in iter_requests(open(logfile)):
        print request
