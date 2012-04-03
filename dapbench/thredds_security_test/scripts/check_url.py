'''
Created on 28 Sep 2011

@author: rwilkinson
'''
from thredds_security_test.lib.configuration import Configuration
import thredds_security_test.lib.httpget as httpget
from optparse import OptionParser
import os

def main():
    '''Utility to check access to a URL by the current user and optionally to return the data
    retrieved from the URL.
    '''
    parser = OptionParser(usage="%prog [options] url")
    parser.add_option("-k", "--private-key", dest="key_file", metavar="FILE",
                      default=None,
                      help="Private key file.")
    parser.add_option("-c", "--certificate", dest="cert_file", metavar="FILE",
                      default=os.path.expanduser("~/.esg/credentials.pem"),
                      help="Certificate file.")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
                      help="Print debug information.")
    parser.add_option("-f", "--fetch", dest="output_file", metavar="FILE",
                      default=None, help="Output file.")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    url = args[0]
    # If a private key file is not specified, the key is assumed to be stored in the certificate file.
    config = Configuration(options.key_file if options.key_file and os.path.exists(options.key_file) else None,
                           options.cert_file if options.cert_file and os.path.exists(options.cert_file) else None,
                           options.debug)
    if options.output_file:
        (return_code, return_message, success) = httpget.fetch_from_url_to_file(url, config,
            options.output_file)
    else:
        (return_code, return_message, success) = httpget.check_url(url, config)
    print return_code, return_message

if __name__=='__main__':
    main()
