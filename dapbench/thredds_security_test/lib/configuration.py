'''
Checker configuration class.

Created on 29 Sep 2011

@author: rwilkinson
'''
class Configuration(object):
    """Checker configuration.
    """
    def __init__(self, key_file, cert_file, debug, recurse=False, listonly=False, quiet=False,
                 services_to_test="", service_extensions=None, public_service_extensions=None,
                 forbidden_service_extensions=None, required_container_properties=None,
                 required_file_properties=None):
        """
        @param key_file - file containing the user's private key
        @param cert_file - file containing the user's certificate
        @param services_to_test - list of service types for which to test access
        @param debug - if True, output debugging information
        @param recurse - if True, recurse into linked catalogs
        @param listonly - if True, only list datasets, otherwise check access
        @param quiet - if True, produce minimal output
        @param service_extensions - extensions for services that can have multiple extensions
        @param public_service_extensions - service types and extensions for which public access is
            expected
        @param forbidden_service_extensions - service types and extensions for which no access is
            expected
        @param required_container_properties - dataset properties required for container datasets
        @param required_file_properties - dataset properties required for file datasets
        """
        self.key_file = key_file
        self.cert_file = cert_file
        self.services_to_test = (
            [s.strip() for s in services_to_test.split(',')] if services_to_test else [])
        self.debug = debug
        self.recurse = recurse
        self.listonly = listonly
        self.quiet = quiet
        self.service_extensions = self.parse_dict_of_lists(service_extensions)
        self.public_service_extensions = self.parse_dict_of_lists(public_service_extensions)
        self.forbidden_service_extensions = self.parse_dict_of_lists(forbidden_service_extensions)
        self.required_container_properties = (
            [p.strip() for p in required_container_properties.split(',')]
            if required_container_properties else [])
        self.required_file_properties = (
            [p.strip() for p in required_file_properties.split(',')]
            if required_file_properties else [])

    @staticmethod
    def parse_dict_of_lists(in_str):
        """Parses a string in the format key1:item11,item12,...;key2:item21,item22...;...
        into a dict with keys key1, key2, ... and values lists [item11, item12] and so on.
        @param in_str - string to parse
        @return dict of lists of items
        """
        result = {}
        if in_str is not None:
            outer_list = in_str.split(';')
            for item in outer_list:
                (key, sep, inner_str) = item.partition(':')
                inner_list = inner_str.split(',')
                result[key] = inner_list
        return result
