# BSD Licence
# Copyright (c) 2012, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

'''
Functions to check access to THREDDS datasets.

Created on 26 Sep 2011

@author: rwilkinson
'''
from dapbench.thredds.lib.catalog_parser import CatalogParser
from dapbench.thredds.lib.dataset_config import Access
import dapbench.thredds.lib.httpget as httpget
from dapbench.thredds.lib.results import Results
import dapbench.thredds.lib.url_util as url_util

SERVICE_TYPES_RETURNING_CATALOGS = ['Catalog', 'Resolver']
SERVICE_TYPES_NOT_TO_CHECK = ['QueryCapability']

def check_catalog(url, config):
    """Checks access to the contents of a THREDDS catalog specified by the URL of a catalog XML
    file.
    @param url - URL of catalog XML file
    @param config - configuration
    @return accumulated results of check
    """
    results = Results()
    _check_catalog(url, config, results)
    return results

def _check_catalog(url, config, results):
    """Checks access to the contents of a THREDDS catalog specified by the URL of a catalog XML
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

    for d in cat.get_datasets():
        service = service_map.get(d.service_name, None)
        if (not service
                or ((service.service_type not in SERVICE_TYPES_RETURNING_CATALOGS)
                    and (service.service_type not in SERVICE_TYPES_NOT_TO_CHECK))):
            if not config.quiet:
                print("Dataset: %s" % d.name)
            if not config.listonly:
                check_dataset(base_url, service_map, d, config, results)

    if config.recurse:
        for d in cat.get_datasets():
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

def check_dataset(base_url, service_map, dataset, config, results):
    """Checks access to a THREDDS dataset by all configured access methods.
    @param base_url - base URL of the catalog
    @param service_map - map of service names to service configurations read from the catalog
    @param config - configuration
    @param results - accumulated results of check
    """
    dataset_results = Results()
    for access in dataset.get_accesses():
        check_access(base_url, service_map, access, config, dataset_results)

    if dataset_results.inconsistent_count:
        results.add_inconsistent()
    else:
        if dataset_results.access_allowed_count + dataset_results.access_denied_count > 0:
            if dataset_results.access_denied_count == 0:
                results.add_access_allowed()
            elif dataset_results.access_allowed_count == 0:
                results.add_access_denied()
            else:
                results.add_inconsistent()
    if dataset_results.untested_count:
        results.add_untested()
    for st in dataset_results.untested_service_types:
        results.add_untested_service_type(st)

def check_access(base_url, service_map, access, config, results):
    """Checks access to a THREDDS dataset with specified access details. If the service type is
    Compound, it calls this function recursively.
    @param base_url - base URL of the catalog
    @param service_map - map of service names to service configurations read from the catalog
    @param access - dataset access details
    @param config - configuration
    @param results - accumulated results of check
    """
    service_name = access.service_name
    if service_name in service_map:
        service = service_map[service_name]
        if service.service_type == 'Compound':
            for child_service in service.children:
                check_access(base_url, service_map, Access(access.url_path, child_service.name),
                             config, results)
        else:
            check_single_access(base_url, service, access, config, results)

def check_single_access(base_url, service, access, config, results):
    """Checks access to a THREDDS dataset with specified access details for a single service, i.e.,
    for a a service type that is not Compound.
    @param base_url - base URL of the catalog
    @param service_map - map of service names to service configurations read from the catalog
    @param access - dataset access details
    @param config - configuration
    @param results - accumulated results of check
    """
    if service.service_type not in config.services_to_test:
        results.add_untested()
        results.add_untested_service_type(service.service_type)
        if not config.quiet:
            print("### Service of type %s not tested." % service.service_type)
        return

    access_allowed_count = 0
    access_denied_count = 0
    inconsistent = False
    extensions = [''] if service.extensions is None else service.extensions
    url = url_util.make_url(base_url, service.base_url) + access.url_path + service.suffix
    for extension in extensions:
        extended_url = url + extension
        (rc, msg, success) = httpget.check_url(extended_url, config)
        if not config.quiet:
            print("  %d  [%s]  %s" % (rc, msg, extended_url))
        if service.is_public(extension):
            if not success:
                inconsistent = True
                if not config.quiet:
                    print("### Expected access allowed.")
        elif service.is_forbidden(extension):
            if success:
                inconsistent = True
                if not config.quiet:
                    print("### Expected access denied.")
        else:
            if success:
                access_allowed_count += 1
            else:
                access_denied_count += 1

    if access_allowed_count + access_denied_count > 0:
        if access_denied_count == 0:
            results.add_access_allowed()
        elif access_allowed_count == 0:
            results.add_access_denied()
        else:
            inconsistent = True
            if not config.quiet:
                print("### Expected accesses either all allowed or all denied (excluding public and forbidden).")
    if inconsistent:
        results.add_inconsistent()
