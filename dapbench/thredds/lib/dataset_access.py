# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

'''
Created on 26 Sep 2011

@author: rwilkinson
'''
from optparse import OptionParser
import os
from dapbench.thredds.lib.configuration import Configuration
from dapbench.thredds.lib.service_config import Service
import dapbench.thredds.lib.httpget as httpget

def configure_services():
    services = [
        Service("odap", "OPENDAP", "/thredds/dodsC/", "", [".html", ".dds", ".das", ".asc", ".dods"]),
        Service("http", "HTTPServer", "/thredds/fileServer/", "", None)
    ]
    return services

def check_dataset(base_url, dataset_path, services, config):
    for service in services:
        print service.name, service.service_type
        extensions = [''] if service.extensions is None else service.extensions
        for extension in extensions:
            url = base_url + service.base_url + dataset_path + extension
            (rc, msg, success) = httpget.check_url(url, config)
            print("  %d  %s" % (rc, url))

if __name__ == '__main__':
    """Checks accessibility of a dataset to the user by HTTPServer and OPENDAP services.
    """
    parser = OptionParser(usage="%prog [options] base_url dataset_path")
    parser.add_option("-k", "--private-key", dest="key_file", metavar="FILE",
                      default=os.path.expanduser("~/.esg/credentials.pem"),
                      help="Private key file.")
    parser.add_option("-c", "--certificate", dest="cert_file", metavar="FILE",
                      default=os.path.expanduser("~/.esg/credentials.pem"),
                      help="Certificate file.")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="Print debug information.")
    parser.add_option("-s", "--services-to-test", dest="services_to_test",
                      default="HTTPServer,OPENDAP",
                      help="Service types to test")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Incorrect number of arguments")

    base_url = args[0]
    dataset_path = args[1]
    config = Configuration(options.key_file, options.cert_file, options.debug, services_to_test=options.services_to_test)

    services = configure_services()

    check_dataset(base_url, dataset_path, services, config)
