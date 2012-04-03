# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

'''
Dataset and enclosed access entities.

Created on 26 Sep 2011

@author: rwilkinson
'''
class Dataset(object):
    '''Dataset entity as read from a THREDDS catalog.
    '''
    def __init__(self, name, url_path, service_name):
        """
        @param name - name attribute
        @param url_path - urlPath attribute
        @param service_name - name of service applicable to the dataset
        """
        self.name = name
        self.url_path = url_path
        self.service_name = service_name
        self.access = []
        self.properties = {}
        self.is_container = False

    def get_accesses(self):
        """Returns access entities for the default service/URL and for each additional access
        method.
        @return list of access entities
        """
        accesses = []
        if self.service_name and self.url_path:
            accesses.append(Access(self.url_path, self.service_name))
        accesses.extend(self.access)
        return accesses

    def __str__(self):
        return ("'%s'  '%s'  '%s'  '%s'" % (self.name, self.url_path, self.service_name, [a.__str__() for a in self.access]))

class Access(object):
    '''Access entity as read from a THREDDS catalog.
    '''
    def __init__(self, url_path, service_name):
        """
        @param url_path - URL path
        @param service_name - name of service
        """
        self.url_path = url_path
        self.service_name = service_name

    def __str__(self):
        return ("'%s'  '%s'" % (self.url_path, self.service_name))

class CatalogRef(object):
    '''Catalog ref entity as read from a THREDDS catalog.
    '''
    def __init__(self, href, title, url):
        self.href = href
        self.title = title
        self.url = url

    def __str__(self):
        return ("'%s'  '%s'  '%s'" % (self.href, self.title, self.url))
        