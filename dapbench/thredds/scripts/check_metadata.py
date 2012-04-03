# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

'''
Created on 28 Oct 2011

@author: rwilkinson
'''
from optparse import OptionParser
import os
import sys
import dapbench.thredds.lib.metadata_finder as metadata_finder
from dapbench.thredds.lib.configuration import Configuration

def main():
    '''Utility to report on the presence of expected dataset properties in a THREDDS catalog.
    Returns statuses:
    0 - completed with no unexpected results
    1 - completed with unexpected results
    2 - user terminated before completion
    '''
    parser = OptionParser(usage="%prog [options] catalog_url")
    parser.add_option("-k", "--private-key", dest="key_file", metavar="FILE",
                      default=None,
                      help="Private key file")
    parser.add_option("-c", "--certificate", dest="cert_file", metavar="FILE",
                      default=os.path.expanduser("~/.esg/credentials.pem"),
                      help="Certificate file")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="Print debug information.")
    parser.add_option("-l", "--list-only", action="store_true", dest="listonly", default=False,
                      help="Only list datasets without checking access.")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
                      help="Produce minimal output.")
    parser.add_option("-r", "--recurse", action="store_true", dest="recurse", default=False,
                      help="Recurse into referenced catalogs.")
    parser.add_option("-n", "--container-properties", dest="required_container_properties",
                      default='drs_id',
                      help="Dataset properties required for container datasets.")
    parser.add_option("-f", "--file-properties", dest="required_file_properties",
                      default='checksum,tracking_id',
                      help="Dataset properties required for file datasets.")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    url = args[0]
    # If a private key file is not specified, the key is assumed to be stored in the certificate file.
    config = Configuration(options.key_file if options.key_file and os.path.exists(options.key_file) else None,
                           options.cert_file if options.cert_file and os.path.exists(options.cert_file) else None,
                           options.debug, options.recurse,
                           options.listonly, options.quiet,
                           required_container_properties=options.required_container_properties,
                           required_file_properties=options.required_file_properties)

    return_status = 0
    try:
        results = metadata_finder.check_catalog(url, config)
        if not options.listonly:
            for prop in results.expected_property_counts.iterkeys():
                print("Propterty: %s    Expected: %d    Found: %d" %
                      (prop, results.expected_property_counts[prop], results.found_property_counts[prop]))
            if results.inconsistent_count > 0:
                print("### Unexpected result ###: Total number of missing properties: %d" %
                      results.inconsistent_count)
                return_status = 1

    except KeyboardInterrupt:
        print 'Terminated by user'
        return_status = 2

    sys.exit(return_status)

if __name__=='__main__':
    main()
