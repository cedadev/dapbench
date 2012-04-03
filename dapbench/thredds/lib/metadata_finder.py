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
from dapbench.thredds.lib.catalog_parser import CatalogParser
import dapbench.thredds.lib.httpget as httpget
import dapbench.thredds.lib.url_util as url_util
from dapbench.thredds.lib.catalog_access import SERVICE_TYPES_RETURNING_CATALOGS

class Results(object):
    """Holds the results summary of the metadata checks.
    """
    def __init__(self):
        self.expected_property_counts = {}
        self.found_property_counts = {}
        self.inconsistent_count = 0

    def add_inconsistent(self):
        self.inconsistent_count += 1

    def add_property_result(self, name, found):
        """Adds a result of checking for a property.
        @param name - name of property
        @param found - boolean indicating whether the property was found
        """
        if name in self.expected_property_counts:
            self.expected_property_counts[name] += 1
        else:
            self.expected_property_counts[name] = 1

        increment = 1 if found else 0
        if name in self.found_property_counts:
            self.found_property_counts[name] += increment
        else:
            self.found_property_counts[name] = increment

        if not found:
            self.add_inconsistent()

def check_catalog(url, config):
    """Checks for rqeuired properties in a THREDDS catalog specified by the URL of a catalog XML
    file.
    @param url - URL of catalog XML file
    @param config - configuration
    @return accumulated results of check
    """
    results = Results()
    _check_catalog(url, config, results)
    return results

def _check_catalog(url, config, results):
    """Checks for rqeuired properties in a THREDDS catalog specified by the URL of a catalog XML
    file - may be called recursively.
    @param url - URL of catalog XML file
    @param config - configuration
    @param results - accumulated results of check
    """
    base_url = url_util.get_base_url(url)
    try:
        catalog_xml = httpget.fetch_from_url(url, config)
    except Exception, exc:
        print("### Could not retrieve catalog %s: %s" % (url, exc.__str__()))
        return
    cat = CatalogParser(catalog_xml)
    service_map = {}
    for s in cat.get_services(config.service_extensions, config.public_service_extensions,
                              config.forbidden_service_extensions):
        service_map[s.name] = s
        for c in s.children:
            service_map[c.name] = c

    required_properties = config.required_container_properties + config.required_file_properties
    for d in cat.get_datasets(required_properties):
        if not config.quiet:
            print("Dataset: %s" % d.name)
        if not config.listonly:
            check_dataset(service_map, d, config, results)

    if config.recurse:
        for d in cat.get_datasets(required_properties):
            service = service_map.get(d.service_name, None)
            if service and service.service_type in SERVICE_TYPES_RETURNING_CATALOGS:
                ref_url = url_util.make_url(base_url, d.url_path)
                if not config.quiet:
                    print("Dataset: %s  Catalog ref: %s" % (d.name, ref_url))
                _check_catalog(ref_url, config, results)

        for c in cat.get_catalog_refs(base_url):
            if not config.quiet:
                print("Catalog ref: %s" % c.url)
            _check_catalog(c.url, config, results)

def check_dataset(service_map, dataset, config, results):
    """Checks for rqeuired properties in a dataset in a THREDDS catalog.
    @param service_map - map of service names to service configurations read from the catalog
    @param dataset - dataset
    @param config - configuration
    @param results - accumulated results of check
    """
    if not config.quiet:
        for prop in config.required_container_properties + config.required_file_properties:
            print("  Property: %s = %s" % (prop, dataset.properties.get(prop, '')))
    if dataset.is_container:
        for prop in config.required_container_properties:
            value_present = True if dataset.properties.get(prop, '') else False
            results.add_property_result(prop, value_present)
            if not value_present:
                print('### Property "%s" not found for dataset %s' % (prop, dataset.name))
    elif _is_dataset_file(dataset, service_map):
        for prop in config.required_file_properties:
            value_present = True if dataset.properties.get(prop, '') else False
            results.add_property_result(prop, value_present)
            if not value_present:
                print('### Property "%s" not found for dataset %s' % (prop, dataset.name))

def _is_dataset_file(dataset, service_map):
    """Determines whether a dataset corresponds to a file on the basis of whether it has an
    HTTPServer access method.
    @param dataset - dataset
    @param service_map - map of service names to service configurations read from the catalog
    """
    for access in dataset.get_accesses():
        if service_map.get(access.service_name, '').service_type == 'HTTPServer':
            return True
    return False
