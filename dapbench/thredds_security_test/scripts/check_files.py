'''
Created on 5 Oct 2011

@author: rwilkinson
'''
from thredds_security_test.lib.configuration import Configuration
import thredds_security_test.lib.file_access as file_access
from optparse import OptionParser
import os
import sys

def main():
    '''Utility to check access to a URL by the current user and optionally to return the data
    retrieved from the URL.
    '''
    parser = OptionParser(usage="%prog [options] list_file_path")
    parser.add_option("-k", "--private-key", dest="key_file", metavar="FILE",
                      default=None,
                      help="Private key file.")
    parser.add_option("-c", "--certificate", dest="cert_file", metavar="FILE",
                      default=os.path.expanduser("~/.esg/credentials.pem"),
                      help="Certificate file.")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="Print debug information.")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
                      help="Produce minimal output.")
    parser.add_option("-a", "--expect-allowed", dest="expect_allowed", type="int", metavar="NUMBER",
                      default=None,
                      help="Number of files for which access is expected to be allowed.")
    parser.add_option("-x", "--expect-denied", dest="expect_denied", type="int", metavar="NUMBER",
                      default=None,
                      help="Number of files for which access is expected to be denied.")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    file_list_path = args[0]
    # If a private key file is not specified, the key is assumed to be stored in the certificate file.
    config = Configuration(options.key_file if options.key_file and os.path.exists(options.key_file) else None,
                           options.cert_file if options.cert_file and os.path.exists(options.cert_file) else None,
                           options.debug, quiet=options.quiet)

    list_file = open(file_list_path, "r")
    file_list = []
    for line in list_file:
        file_list.append(line.strip(' \t\r\n'))
    list_file.close()

    return_status = 0
    try:
        results = file_access.check_files(file_list, config)
        print("Access allowed: %d    Access denied: %d" %
              (results.access_allowed_count, results.access_denied_count))

        if (((options.expect_allowed is not None)
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
