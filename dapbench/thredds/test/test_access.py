# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

'''
Created on 30 Sep 2011

@author: rwilkinson
'''
import os
import unittest
import dapbench.thredds.lib.catalog_access as catalog_access
from dapbench.thredds.lib.configuration import Configuration
from dapbench.thredds.lib.results import Results

class Test(unittest.TestCase):
    """Example test of access to catalogs.
    """
    def setUp(self):
        self.config = Configuration(key_file=os.path.expanduser("~/.esg/credentials.pem"),
                                    cert_file=os.path.expanduser("~/.esg/credentials.pem"),
                                    debug=False,
                                    recurse=False,
                                    listonly=False,
                                    quiet=False,
                                    services_to_test="HTTPServer,OPENDAP",
                                    service_extensions="OPENDAP:.html,.dds,.das,.asc,.ascii,.dods",
                                    public_service_extensions="OPENDAP:.html",
                                    forbidden_service_extensions="OPENDAP:.asc")

    def tearDown(self):
        pass

    def test_catalog(self):
        results = catalog_access.check_catalog(
            "http://ice.badc.rl.ac.uk:8080/thredds/catalog.xml", self.config)
        expected = Results(2, 0)
        self.failUnlessEqual(results, expected)

    def test_testAll(self):
        results = catalog_access.check_catalog(
            "http://ice.badc.rl.ac.uk:8080/thredds/catalog/testAll/catalog.xml", self.config)
        expected = Results(4, 0)
        self.failUnlessEqual(results, expected)

    def test_testAll2(self):
        results = catalog_access.check_catalog(
            "http://ice.badc.rl.ac.uk:8080/thredds/catalog/testAll2/catalog.xml", self.config)
        expected = Results(0, 4)
        self.failUnlessEqual(results, expected)

    def test_enhancedCatalog(self):
        config = Configuration(key_file=os.path.expanduser("~/.esg/credentials.pem"),
            cert_file=os.path.expanduser("~/.esg/credentials.pem"),
            debug=False,
            recurse=True,
            listonly=False,
            quiet=False,
            services_to_test="HTTPServer,OPENDAP",
            service_extensions="OPENDAP:.html,.dds,.das,.asc,.ascii,.dods",
            public_service_extensions="OPENDAP:.html",
            forbidden_service_extensions="OPENDAP:.asc")
        results = catalog_access.check_catalog(
            "http://ice.badc.rl.ac.uk:8080/thredds/enhancedCatalog.xml", config)
        expected = Results(0, 5)
        self.failUnlessEqual(results, expected)

if __name__ == "__main__":
    unittest.main()
