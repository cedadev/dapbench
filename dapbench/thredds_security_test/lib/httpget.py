'''
Checks access to a URL, optionally returning data.

Created on 21 Sep 2011

@author: rwilkinson
'''
import cookielib
import httplib
import os
import urllib2
import urlparse

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    '''Extension of HTTPSHandler that provides key and certificate for certificate authentication.
    '''
    def __init__(self, key_file, cert_file, debuglevel=0):
        """
        @param key_file - location of user's private key file
        @param cert_file - location of user's certificate key file
        @param debuglevel - debug level for HTTPSHandler
        """
        urllib2.HTTPSHandler.__init__(self, debuglevel)
        self.key_file = key_file
        self.cert_file = cert_file

    def https_open(self, req):
        """Opens HTTPS request
        @param req - HTTP request
        @return HTTP Response object
        """
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        """Gets connection
        @param host - host name or address + port
        @param timeout - timeout
        @return HTTPS connection
        """
        return httplib.HTTPSConnection(host, timeout=timeout, key_file=self.key_file,
                                       cert_file=self.cert_file)

def check_url(url, config):
    """Checks accessibility of a URL.
    @param url - URL to attempt to open
    @param config - configuration
    @return tuple (
        returned HTTP status code or 0 if an error occurred
        returned message
        boolean indicating whether access was successful
    )
    """
    (return_code, return_message, response) = open_url(url, config)
    if response:
        response.close()

    return (return_code, return_message, (return_code == httplib.OK))

def fetch_from_url(url, config):
    """Returns data retrieved from a URL.
    @param url - URL to attempt to open
    @param config - configuration
    @return data retrieved from URL or None
    """
    (return_code, return_message, response) = open_url(url, config)
    if return_code and return_code == httplib.OK:
        return_data = response.read()
        response.close()
        return return_data
    else:
        raise Exception(return_message)

def fetch_from_url_to_file(url, config, output_file):
    """Writes data retrieved from a URL to a file.
    @param url - URL to attempt to open
    @param config - configuration
    @param output_file - output file
    @return tuple (
        returned HTTP status code or 0 if an error occurred
        returned message
        boolean indicating whether access was successful
    )
    """
    (return_code, return_message, response) = open_url(url, config)
    if return_code == httplib.OK:
        return_data = response.read()
        response.close()
        outfile = open(output_file, "w")
        outfile.write(return_data)
        outfile.close()
    return (return_code, return_message, (return_code == httplib.OK))

def open_url(url, config):
    """Attempts to open a connection to a specified URL.
    @param url - URL to attempt to open
    @param config - configuration
    @return tuple (
        returned HTTP status code or 0 if an error occurred
        returned message or error description
        response object
    )
    """
    debuglevel = 1 if config.debug else 0

    # Set up handlers for URL opener.
    cj = cookielib.CookieJar()
    http_handler = urllib2.HTTPHandler(debuglevel=debuglevel)
    cookie_handler = urllib2.HTTPCookieProcessor(cj)
    client_auth_handler = HTTPSClientAuthHandler(config.key_file, config.cert_file, debuglevel=debuglevel)

    handlers = [http_handler,
                cookie_handler,
                client_auth_handler]

    # Explicitly remove proxy handling if the host is one listed in the value of the no_proxy
    # environment variable because urllib2 does use proxy settings set via http_proxy and
    # https_proxy, but does not take the no_proxy value into account.
    if not _should_use_proxy(url):
        handlers.append(urllib2.ProxyHandler({}))
        if config.debug:
            print "Not using proxy"

    opener = urllib2.build_opener(*handlers)

    # Open the URL and check the response.
    return_code = 0
    return_message = ''
    response = None
    try:
        response = opener.open(url)
        if response.url == url:
            return_message = response.msg
            return_code = response.code
        else:
            return_message = ('Redirected (%s  %s)' % (response.code, response.url))
        if config.debug:
            for index, cookie in enumerate(cj):
                print index, '  :  ', cookie        
    except urllib2.HTTPError, exc:
        return_code = exc.code
        return_message = ("Error: %s" % exc.msg)
        if config.debug:
            print exc.code, exc.msg
    except Exception, exc:
        return_message = ("Error: %s" % exc.__str__())
        if config.debug:
            print exc.__class__, exc.__str__()
    return (return_code, return_message, response)

def _should_use_proxy(url):
    """Determines whether a proxy should be used to open a connection to the specified URL, based on
        the value of the no_proxy environment variable.
    @param url - URL string
    """
    no_proxy   = os.environ.get('no_proxy', '')

    urlObj = urlparse.urlparse(url)
    for np in [h.strip() for h in no_proxy.split(',')]:
        if urlObj.hostname == np:
            return False

    return True
