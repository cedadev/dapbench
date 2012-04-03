'''
Functions for manipulating URLs.

Created on 27 Sep 2011

@author: rwilkinson
'''
import urlparse

def get_base_url(url):
    """Returns the base part of a URL, i.e., excluding any characters after the last /.
    @param url - URL to process
    @return base URL
    """
    parts = url.rpartition('/')
    return parts[0] + (parts[1] if len(parts) >= 2 else '')

def get_server_url(url):
    """Returns the part of a URL specifying the server, i.e., the schema and net location.
    @param url - URL to process
    @return server URL
    """
    parts = urlparse.urlparse(url)
    return urlparse.urlunparse((parts.scheme, parts.netloc, '', '', '', ''))

def is_relative(url):
    """Determines whether a URL or URL fragment is relative, i.e., does not start with a scheme and
        net location and does not start with a /.
    @param url - URL to process
    @return True if URL is relative, else False
    """
    parts = urlparse.urlparse(url)
    return not (parts.scheme or parts.netloc or url.startswith('/'))

def is_server_relative(url):
    """Determines whether a URL or URL fragment is relative to a server location, i.e., does not
        start with a scheme and net location and but does start with a /.
    @param url - URL to process
    @return True if URL is relative to server, else False
    """
    parts = urlparse.urlparse(url)
    return not (parts.scheme or parts.netloc) and url.startswith('/')

def make_url(base_url, url):
    """Combines a URL with a base URL as follows:
    If the URL is absolute (contains a scheme and net location) return the URL.
    If the URL is relative (does not contain a scheme and net location and does not begin with a /)
        return the base URL followed by the URL.
    If the URL is relative is relative to the server location (does not contain a scheme and net
        location and begins with a /) return the scheme and net location from the base URL followed
        by the URL.
    @param base_url - base URL
    @param url - URL
    @return combined URL
    """
    if is_relative(url):
        return_url = base_url + url
    elif is_server_relative(url):
        return_url = get_server_url(base_url) + url
    else:
        return_url = url
    return return_url
