'''
Created on 27 Sep 2011

@author: rwilkinson
'''
from optparse import OptionParser
import os
import sys
import dapbench.thredds.lib.catalog_access as catalog_access
from dapbench.thredds.lib.configuration import Configuration

def main():
    '''Utility to report on the ability of the user to access datasets in a THREDDS system.
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
    parser.add_option("-a", "--expect-allowed", dest="expect_allowed", type="int", metavar="NUMBER",
                      default=None,
                      help="Number of datasets for which access is expected to be allowed")
    parser.add_option("-x", "--expect-denied", dest="expect_denied", type="int", metavar="NUMBER",
                      default=None,
                      help="Number of datasets for which access is expected to be denied")
    parser.add_option("-s", "--services-to-test", dest="services_to_test",
                      default="HTTPServer,OPENDAP",
                      help="Service types to test")
    parser.add_option("-e", "--service-extensions", dest="service_extensions",
                      default="OPENDAP:.html,.dds,.das,.asc,.ascii,.dods",
                      help="Extensions used by service types, e.g., OPENDAP:.html,.dds;OtherSvc:.dat,.asc")
    parser.add_option("-p", "--public-service-extensions", dest="public_service_extensions",
                      default="OPENDAP:.html",
                      help="Service types and extensions for which public access is expected, e.g., OPENDAP:.html,.dds")
    parser.add_option("-f", "--forbidden-service-extensions", dest="forbidden_service_extensions",
                      default=None,
                      help="Service types and extensions for which no access is expected, e.g., OPENDAP:.asc")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    url = args[0]
    # If a private key file is not specified, the key is assumed to be stored in the certificate file.
    config = Configuration(options.key_file if options.key_file and os.path.exists(options.key_file) else None,
                           options.cert_file if options.cert_file and os.path.exists(options.cert_file) else None,
                           options.debug, options.recurse,
                           options.listonly, options.quiet, options.services_to_test,
                           options.service_extensions, options.public_service_extensions,
                           options.forbidden_service_extensions)

    return_status = 0
    try:
        results = catalog_access.check_catalog(url, config)
        if not options.listonly:
            print("Access allowed: %d    Access denied: %d    Inconsistent: %d    Untested: %d  (%s)" %
                  (results.access_allowed_count, results.access_denied_count,
                   results.inconsistent_count, results.untested_count,
                   ', '.join(results.untested_service_types)))
            if results.inconsistent_count > 0:
                print "### Unexpected result ###"
                return_status = 1
            elif (((options.expect_allowed is not None)
                    and (results.access_allowed_count != options.expect_allowed))
                or ((options.expect_denied is not None)
                    and (results.access_denied_count != options.expect_denied))):
                print "### Unexpected result ###"
                return_status = 1

    except KeyboardInterrupt:
        print 'Terminated by user'
        return_status = 2

    sys.exit(return_status)

if __name__=='__main__':
    main()
