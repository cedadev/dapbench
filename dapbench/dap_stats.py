"""
Statistics on dap requests
"""

import numpy
import sys

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
        if self.last_request:
            ds_stat = self.datasets.setdefault(self.last_request.dataset, [])
            ds_stat.append((self.last_timestamp, timestamp, self.last_request))


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
                print '%s\t%d\t%f\t%d' % (resp, count, tmean, smean)
        print

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

