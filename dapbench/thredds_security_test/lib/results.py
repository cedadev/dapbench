'''
Checker results class

Created on 29 Sep 2011

@author: rwilkinson
'''
import bisect

class Results(object):
    def __init__(self, access_allowed_count=0, access_denied_count=0, inconsistent_count=0,
                 untested_count=0):
        self.access_allowed_count = access_allowed_count
        self.access_denied_count = access_denied_count
        self.inconsistent_count = inconsistent_count
        self.untested_count = untested_count
        self.untested_service_types = []

    def add_access_allowed(self):
        self.access_allowed_count += 1

    def add_access_denied(self):
        self.access_denied_count += 1

    def add_inconsistent(self):
        self.inconsistent_count += 1

    def add_untested(self):
        self.untested_count += 1

    def add_untested_service_type(self, service_type):
        """Add a service type to a sorted list.
        """
        if service_type not in self.untested_service_types:
            bisect.insort(self.untested_service_types, service_type)

    def __eq__(self, other):
        return (isinstance(other, Results)
                and (self.access_allowed_count == other.access_allowed_count)
                and (self.access_denied_count == other.access_denied_count)
                and (self.inconsistent_count == other.inconsistent_count)
                and (self.untested_count == other.untested_count)
                and (self.untested_service_types == other.untested_service_types))

    def __repr__(self):
        return("(allowed=%d, denied=%d, inconsistent=%d, untested=%d %s)" %
               (self.access_allowed_count, self.access_denied_count, self.inconsistent_count,
                self.untested_count, self.untested_service_types.__str__()))
