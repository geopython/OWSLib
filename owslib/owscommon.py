 
# =============================================================================
# OWSLib. Copyright (C) 2005 Sean C. Gillies
#
# Contact email: sgillies@frii.com
#Author: Dominic Lowe <dominic.lowe@stfc.ac.uk>
#owscommon.py set of classes representing OWSCommon 
# =============================================================================

from owslib.util import nspath, testXMLValue

XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'


class ServiceIdentification(object):
    ''' Implements IServiceIdentificationMetadata, initialize with <ows:ServiceIdentification> element'''
    def __init__(self, serviceIdentificationElem, version):
        self._root=serviceIdentificationElem
        self.service='OGC:WFS'
        self.type=testXMLValue(self._root.find(nspath('ServiceType')))
        self.service=self.type #alternative? keep both?
        self.version = testXMLValue(self._root.find(nspath('ServiceTypeVersion')))
        self.type=self.service
        self.version = version        
        self.title = testXMLValue(self._root.find(nspath('Title')))       
        self.abstract = testXMLValue(self._root.find(nspath('Abstract')))       
        self.keywords = [f.text for f in self._root.findall(nspath('Keywords'))]
        self.accessconstraints=testXMLValue(self._root.find(nspath('AccessConstraints')))
        self.fees = testXMLValue(self._root.find(nspath('Fees')))

class ServiceProvider(object):
    ''' Implements IServiceProviderMetatdata '''
    def __init__(self, infoset):
        self._root=infoset
        self.name=testXMLValue(self._root.find(nspath('ProviderName')))
        val = self._root.find(nspath('ProviderSite'))
        if val is not None:
            urlattrib=val.attrib[nspath('href', XLINK_NAMESPACE)]
            self.url = testXMLValue(urlattrib, True)
        else:
            self.url =None
      
        #contact details defined in ContactMetadata class:
        contact = self._root.find(nspath('ServiceContact'))        
        # sometimes there is a contact block that is empty, so make
        # sure there are children to parse
        if contact is not None and contact[:]:
            self.contact = ContactMetadata(contact)
        else:
            self.contact = None

class ContactMetadata:
    """Abstraction for contact details advertised in GetCapabilities.
    Not fully tested due to lack of Contact info in test capabilities doc.
    """
    def __init__(self, elem):
        name = elem.find(nspath('IndividualName'))
        self.test=elem
        self.name=testXMLValue(name)
        self.position=testXMLValue(elem.find(nspath('PositionName')))
        self.organization=testXMLValue(elem.find(nspath('ContactPersonPrimary/ContactOrganization')))
        self.postcode = self.country = None
        address = elem.find(nspath('ContactInfo/Address'))
        if address is not None:
            self.email = testXMLValue(address.find(nspath('ElectronicMailAddress')))
            self.street = testXMLValue(address.find(nspath('DeliveryPoint')))
            self.city = testXMLValue(address.find(nspath('City')))
            self.region = testXMLValue(address.find(nspath('AdministrativeArea')))
            self.postcode = testXMLValue(address.find(nspath('PostalCode')))
            self.country = testXMLValue(address.find(nspath('Country')))


class OperationMetadata:
    """Abstraction for OWS Operations metadata.
    
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.get('name')
        # formatOptions
        self.formatOptions = [f.tag for f in elem.findall(nspath('ResultFormat/*'))]
        methods = []
        for verb in elem.findall(nspath('DCP/HTTP/*')):
            url = verb.attrib['{http://www.w3.org/1999/xlink}href']
            methods.append((verb.tag, {'url': url}))
        self.methods = dict(methods)

