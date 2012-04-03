'''
Parses required details from a THREDDS catalog.

Created on 26 Sep 2011

@author: rwilkinson
'''
import xml.dom.minidom as minidom
from thredds_security_test.lib.dataset_config import Dataset, Access, CatalogRef
from thredds_security_test.lib.service_config import Service
import thredds_security_test.lib.url_util as url_util
import thredds_security_test.lib.xml_util as xml_util

class CatalogParser(object):
    """Parses required details from a THREDDS catalog.
    """
    def __init__(self, xml):
        """
        @param xml - catalog XML as string
        """
        self.dom = minidom.parseString(xml)
        # Get the namespace URI for the document root element.
        self.ns = self.dom.documentElement.namespaceURI

    def get_services(self, service_extensions, public_service_extensions,
                     forbidden_service_extensions, rootElement=None):
        """Gets the service elements from the catalog XML document or optionally those within a
            specified element.
        @param service_extensions - dict of lists of additional extensions for services
        @param public_service_extensions - dict of lists of extensions for services for which access
            is public
        @param forbidden_service_extensions - dict of lists of extensions for services for which
            access is forbidden
        @param rootElement - element within which to find service elements or None to find them
            within the root catalog element.
        @return list of service entities
        """
        root = self.dom.documentElement if rootElement is None else rootElement
        service_elements = xml_util.getChildrenByNameNS(root, self.ns, 'service')
        services = []
        for el in service_elements:
            service_type = el.getAttribute('serviceType')
            service = Service(el.getAttribute('name'),
                              service_type,
                              el.getAttribute('base'),
                              el.getAttribute('suffix'),
                              service_extensions.get(service_type, ['']),
                              public_service_extensions.get(service_type, []),
                              forbidden_service_extensions.get(service_type, []))
            if service_type == 'Compound':
                service.children.extend(self.get_services(
                    service_extensions, public_service_extensions, forbidden_service_extensions, el))
            services.append(service)
        return services

    def get_datasets(self, required_properties=None, rootElement=None, inherited_metadata_service_name=None):
        """Gets the dataset elements from the catalog XML document or optionally those within a
            specified element.
        @param required_properties - list of names of properties the values of which are to be
            retrieved
        @param rootElement - element within which to find dataset elements or None to find them
            within the root catalog element.
        @param inherited_metadata_service_name - service name inherited from the metadata element of
            an enclosing dataset element, or None
        @return list of dataset entities
        """
        root = self.dom.documentElement if rootElement is None else rootElement
        ds_elements = xml_util.getChildrenByNameNS(root, self.ns, 'dataset')
        datasets = []
        for el in ds_elements:
            (service_name, inherited_metadata_service_name) = self.find_dataset_service_name(el, inherited_metadata_service_name)
            dataset = Dataset(el.getAttribute('name'),
                              el.getAttribute('urlPath'),
                              service_name)
            for access_el in xml_util.getChildrenByNameNS(el, self.ns, 'access'):
                dataset.access.append(Access(access_el.getAttribute('urlPath'),
                                             access_el.getAttribute('serviceName')))
            if required_properties:
                for property_el in xml_util.getChildrenByNameNS(el, self.ns, 'property'):
                    name = property_el.getAttribute('name')
                    if name in required_properties:
                        dataset.properties[name] = property_el.getAttribute('value')
            child_datasets = self.get_datasets(required_properties, el, inherited_metadata_service_name)
            dataset.is_container = (len(child_datasets) > 0)
            datasets.append(dataset)

            # Recurse into child datasets.
            datasets.extend(child_datasets)
        return datasets

    def get_catalog_refs(self, base_url, rootElement=None):
        """Gets the catalogRef elements from the catalog XML document or optionally those within a
            specified element.
        @param rootElement - element within which to find dataset elements or None to find them
            within the root catalog element.
        @return list of catalogRef entities
        """
        root = self.dom.documentElement if rootElement is None else rootElement
        cr_elements = xml_util.getChildrenByNameNS(root, self.ns, 'catalogRef')
        catalog_refs = []
        for el in cr_elements:
            ref_url = xml_util.getAttributeByLocalName(el, 'href')
            url = url_util.make_url(base_url, ref_url)
            catalog_ref = CatalogRef(xml_util.getAttributeByLocalName(el, 'href'),
                                     xml_util.getAttributeByLocalName(el, 'title'),
                                     url)

            catalog_refs.append(catalog_ref)

        # Recurse into contained datasets.
        ds_elements = xml_util.getChildrenByNameNS(root, self.ns, 'dataset')
        for ds_element in ds_elements:
            catalog_refs.extend(self.get_catalog_refs(base_url, ds_element))

        return catalog_refs

    def find_dataset_service_name(self, ds_element, inherited_metadata_service_name=None):
        """Find service name according to precedence rules.
        @param ds_element - dataset element for which to find the service name
        @param inherited_metadata_service_name - service name inherited from the metadata element of
            an enclosing dataset element, or None
        @return tuple (
            service_name - service name
            inheritable_metadata_service_name - service name that might be inherited by enclosed
                dataset elements
        )
        """
        service_name = xml_util.getSingleChildTextByNameNS(ds_element, self.ns, 'serviceName')

        metadata_el = xml_util.getSingleChildByNameNS(ds_element, self.ns, 'metadata')
        inheritable_metadata_service_name = None
        if metadata_el is not None:
            inherited_val = metadata_el.getAttribute('inherited')
            inherited = True if inherited_val and inherited_val in ['true', '1'] else False

            metadata_service_name = xml_util.getSingleChildTextByNameNS(metadata_el, self.ns, 'serviceName')
            if not service_name and metadata_service_name:
                service_name = metadata_service_name

            if inherited and metadata_service_name:
                inheritable_metadata_service_name = metadata_service_name

        if not service_name:
            service_name = ds_element.getAttribute('serviceName')  # deprecated in favour of element

        if not service_name and inherited_metadata_service_name:
            service_name = inherited_metadata_service_name

        if not inheritable_metadata_service_name and inherited_metadata_service_name:
            inheritable_metadata_service_name = inherited_metadata_service_name

        return (service_name, inheritable_metadata_service_name)
