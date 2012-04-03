'''
Functions to check access to individual files.

Created on 5 Oct 2011

@author: rwilkinson
'''
import thredds_security_test.lib.httpget as httpget
from thredds_security_test.lib.results import Results

def check_files(file_list, config):
    """Checks access to a list of files.
    @param file_list list of files to check
    @param config - configuration
    @return accumulated results of check
    """
    results = Results()

    for file_url in file_list:
        (rc, msg, success) = httpget.check_url(file_url, config)

        if not config.quiet:
            print("  %d  [%s]  %s" % (rc, msg, file_url))

        if success:
            results.add_access_allowed()
        else:
            results.add_access_denied()

    return results
