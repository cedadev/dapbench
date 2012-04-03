'''
Configuration data for services.

Created on 26 Sep 2011

@author: rwilkinson
'''
class Service(object):
    # Extensions to be appended to URLs for particular services to access different types of data.
    _default_extensions = {
        'OPENDAP': [".html", ".dds", ".das", ".asc", ".ascii", ".dods"],
        'HTTPServer': None
    }

    _default_public_extensions = {
        'OPENDAP': [".html"]
    }

    def __init__(self, name, service_type, base_url, suffix, extensions, public_extensions=None,
                 forbidden_extensions=None):
        """
        @param name - name attribute
        @param service_type - serviceType attribute
        @param base_url - base attribute
        @param suffix - suffix attribute
        @param extensions - extensions to be appended to URLs to override defaults
        @param public_extensions - extensions for which public access is to be assumed
        @param forbidden_extensions - extensions for which no access is to be assumed
        """
        self.name = name
        self.service_type = service_type
        self.base_url = base_url
        self.suffix = suffix
        self.extensions = (extensions if extensions is not None
                           else self._default_extensions.get(service_type, None))
        self.public_extensions = (public_extensions if public_extensions is not None
                                  else self._default_public_extensions.get(service_type, None))
        self.forbidden_extensions = (forbidden_extensions if forbidden_extensions is not None
                                     else None)
        self.children = []

    def is_public(self, extension):
        if self.public_extensions is not None:
            if extension in self.public_extensions:
                return True
        return False

    def is_forbidden(self, extension):
        if self.forbidden_extensions is not None:
            if extension in self.forbidden_extensions:
                return True
        return False

    def __str__(self):
        return ("'%s'  '%s'  '%s'  '%s'  '%s'  '%s'" % (self.name, self.service_type, self.base_url,
                                                        self.suffix, self.extensions.__str__(),
                [s.name for s in self.children]))
