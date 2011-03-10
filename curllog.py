#!/usr/bin/env python
"""
Process a curl verbose log to capture OpenDAP requests.

"""

import re
import sys
import urllib

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
        mo = re.match(r'GET ([^?]*)\.([^?]+)(\?.*)? HTTP/[0-9.]+$', get_request)
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


    def __init__(self, requests=None):
        self.datasets = {}

        self.update(requests)

    def add_req(self, request):
        ds_stat = self.datasets.setdefault(request.dataset, {})
        resp = ds_stat.response
        if resp not in ['das', 'dds', 'dods']:
            resp = '?'
        rlist = ds_stat.setdefault(resp, [])
        rlist.append(request)

        if request.response == 'das':
            ds_stat['das'] += 1
        elif request.response == 'dds':
            ds_stat['dds'] += 1
        elif request.response == 'dods':
            ds_stat['dods'].append(request)
        else:
            ds_stat['?'].append(request)
            
    def update(self, requests):
        for request in requests:
            self.add_req(request)

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
