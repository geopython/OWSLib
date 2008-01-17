# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2007 STFC <http://www.stfc.ac.uk>
#
# Authors : 
#          Dominic Lowe <d.lowe@rl.ac.uk>
#
# Contact email: d.lowe@rl.ac.uk
# =============================================================================


from wcsBase import WCSBase, WCSCapabilitiesReader, CoverageInfo, ServiceInfo, RereadableURL
from urllib import urlencode
from urllib2 import urlopen
from owslib.etree import etree
import os, errno
from owslib.coverage import wcsdecoder

def ns(tag):
    return '{http://www.opengis.net/wcs/1.1}'+tag

class ServiceException(Exception):
    pass

class WebCoverageService_1_1_0(WCSBase):
    """Abstraction for OGC Web Coverage Service (WCS), version 1.1.0
    Implements IWebCoverageService.
    """
    def __init__(self, url, xml):
        self.version='1.1.0'
        self.url = url        
        self._capabilities = None
        # initialize from saved capability document
        if xml:
            reader = WCSCapabilitiesReader(self.version)
            self._capabilities = Capabilities(reader.readString(xml))
          
     
    def _getcapproperty(self):
        if not self._capabilities:            
            reader = WCSCapabilitiesReader(self.version)
            self._capabilities = Capabilities(reader.read(self.url))
        return self._capabilities
    capabilities = property(_getcapproperty, None)
    

    def getcapabilities(self):
        """Request and return capabilities document from the WMS as a 
        file-like object."""
        reader = WCSCapabilitiesReader(self.version)
        u = urlopen(reader.capabilities_url(self.url))
        # check for service exceptions, and return
        if u.info().gettype() == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException, \
                str(se_tree.find('ServiceException').text).strip()
        return u

    def _getSupportedCRS110(self,identifier):
                # version specific method
        crss=[]
        for elem in self.getDescribeCoverage(identifier).findall(ns('CoverageDescription/')+ns('SupportedCRS')):
            crss.append(elem.text)
        return crss
      
    
    def _getSupportedFormats110(self,identifier): #maybe can get this from the capabilites doc?
            # version specific method
        frmts=[]
        for elem in self.getDescribeCoverage(identifier).findall(ns('CoverageDescription/')+ns('SupportedFormat')):
            frmts.append(elem.text)
        return frmts 
             
    def _getTimes(self, identifier):
         timelimits=[]
         for elem in self.getDescribeCoverage(identifier).findall(ns('CoverageDescription/')+ns('Domain/')+ns('TemporalDomain/')+ns('TimePeriod/')):
             subelems=elem.getchildren()
             timelimits=[subelems[0].text,subelems[1].text]
         return timelimits
         
    def _buildGenericCoverages(self):
        genericCoverageList=[]
        for item in self.capabilities.contents:
            ci = CoverageInfo(identifier=item.identifier, labelordescription=item.title, wgs84bbox=item.WGS84BoundingBox)
            ci._supCRS=self._getSupportedCRS110 # version specific method
            ci._supFormats=self._getSupportedFormats110
            ci._times=self._getTimes
            genericCoverageList.append(ci)
        return genericCoverageList
     
    def _buildGenericProviderInfo(self):
        pn=self.capabilities.serviceProvider.providerName
        cn=self.capabilities.serviceProvider.contactName
        #cp=
        #ad=
        #ph=
        #fx=
        #em=
        
        return ProviderInfo(providerName=pn, contactName=cn)
    
    def _getaddressString(self):
        #todo
        address=self.capabilities.serviceProvider.serviceContact.contactInfo.address.deliveryPoint
        return address
        
    def _buildGenericServiceInfo(self):
        ''' enables generic interface'''
        _fees=self.capabilities.serviceIdentification.fees
        _accessConstraints=self.capabilities.serviceIdentification.accessConstraints
        _providerName=self.capabilities.serviceProvider.providerName               
        _contactName=self.capabilities.serviceProvider.serviceContact.individualName
        _contactPosition=self.capabilities.serviceProvider.serviceContact.positionName
        _addressString=self._getaddressString()
        _phone=self.capabilities.serviceProvider.serviceContact.contactInfo.phone.voice
        _fax=self.capabilities.serviceProvider.serviceContact.contactInfo.phone.facsimile
        _email=self.capabilities.serviceProvider.serviceContact.contactInfo.address.email
        return ServiceInfo(fees=_fees, accessConstraints=_accessConstraints ,providerName=_providerName, contactName=_contactName,contactPosition=_contactPosition, addressString=_addressString, phone=_phone, fax=_fax, email=_email)
    
    def getData(self, directory='outputdir', outputfile='coverage.nc',  **kwargs):
        u=self.getCoverageRequest(**kwargs)
        #create the directory if it doesn't exist:
        try:
            os.mkdir(directory)
        except OSError, e:
            # Ignore directory exists error
            if e.errno <> errno.EEXIST:
                raise          
        #elif wcs.version=='1.1.0':
        #Could be multipart mime or XML Coverages document, need to use the decoder...
        decoder=wcsdecoder.WCSDecoder(u)
        x=decoder.getCoverages()
        if type(x) is wcsdecoder.MpartMime:
            filenames=x.unpackToDir(directory)
            #print 'Files from 1.1.0 service written to %s directory'%(directory)
        else:
            filenames=x
        return filenames
    
    
    def getCoverageRequest(self, identifier=None, bbox=None, timeSequence=None, format = None, store=None, method='Get',**kwargs):
        """Request and return a coverage from the WCS as a file-like object
        note: additional **kwargs helps with multi-version implementation
        core keyword arguments should be supported cross version
        example:
        cvg=wcs.getCoverageRequest(identifier=['TuMYrRQ4'], timeSequence=['2792-06-01T00:00:00.0'], bbox=(-112,36,-106,41),format='application/netcdf', store='true')

        is equivalent to:
        http://myhost/mywcs?SERVICE=WCS&REQUEST=GetCoverage&IDENTIFIER=TuMYrRQ4&VERSION=1.1.0&BOUNDINGBOX=-180,-90,180,90&TIMESEQUENCE=[bb&FORMAT=application/netcdf
        
        if store = true, returns a coverages XML file
        if store = false, returns a multipart mime
        

        """
        #use fully qualified namespace
        if method == 'Get':
            method='{http://www.opengis.net/wcs/1.1/ows}Get'
        md = self.capabilities
        base_url = md.getOperationByName('GetCoverage').methods[method]['url']


        #process kwargs
        request = {'version': self.version, 'request': 'GetCoverage', 'service':'WCS'}
        assert len(identifier) > 0
        request['identifier']=identifier
        #request['identifier'] = ','.join(identifier)
        request['boundingbox']=','.join([str(x) for x in bbox])
        request['timesequence']=','.join(timeSequence)
        request['format']=format
        if store is None: store=False
        request['store']=store
        
        #encode and request
        data = urlencode(request)
        u = urlopen(base_url, data=data)
                
        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'text/xml':          
            #going to have to read the xml to see if it's an exception report.
            #wrap the url stram in a extended StringIO object so it's re-readable
            u=RereadableURL(u)      
            se_xml= u.read()
            se_tree = etree.fromstring(se_xml)
            serviceException=se_tree.find('{http://www.opengis.net/ows}Exception')
            if serviceException is not None:
                raise ServiceException, \
                str(serviceException.text).strip()
            u.seek(0)
        return u
        
class OperationMetadata(object):
    """Abstraction for operation metadata    
    Implements IOperationMetadata.
    """
    def __init__(self, elem):
        self.name = elem.get('name')       
        self.formatOptions = [f.text for f in elem.findall('{http://www.opengis.net/wcs/1.1/ows}Parameter/{http://www.opengis.net/wcs/1.1/ows}AllowedValues/{http://www.opengis.net/wcs/1.1/ows}Value')]
        methods = []
        for verb in elem.findall('{http://www.opengis.net/wcs/1.1/ows}DCP/{http://www.opengis.net/wcs/1.1/ows}HTTP/*'):
            url = verb.attrib['{http://www.w3.org/1999/xlink}href']
            methods.append((verb.tag, {'url': url}))
        self.methods = dict(methods)

class ServiceIdentificationMetadata(object):
    """ Abstraction for ServiceIdentification Metadata 
    implements IServiceIdentificationMetadata"""
    def __init__(self,elem):        
        self.service="WCS"
        self.version="1.1.0"
        self.title = elem.find('{http://www.opengis.net/ows}Title').text
        self.abstract = elem.find('{http://www.opengis.net/ows}Abstract').text
        self.keywords = [f.text for f in elem.findall('{http://www.opengis.net/ows}Keywords/{http://www.opengis.net/ows}Keyword')]
        self.rights='' #TODO
        #self.link = elem.find('{http://www.opengis.net/wcs/1.1}Service/{http://www.opengis.net/wcs/1.1}OnlineResource').attrib.get('{http://www.w3.org/1999/xlink}href', '')
               
        #NOTE: do these belong here?
        self.fees=elem.find('{http://www.opengis.net/wcs/1.1/ows}Fees').text
        self.accessConstraints=elem.find('{http://www.opengis.net/wcs/1.1/ows}AccessConstraints').text
       
       
class ServiceProviderMetadata(object):
    """ Abstraction for ServiceProvider metadata 
    implements IServiceProviderMetadata """
    def __init__(self,elem):
        self.provider=elem.find('{http://www.opengis.net/ows}ProviderName').text
        self.contact=ServiceContact(elem.find('{http://www.opengis.net/ows}ServiceContact'))
        self.url='' #URL for provider's web site (string)

class Address(object):
    def __init__(self,elem):
        self.deliveryPoint=elem.find('{http://www.opengis.net/ows}DeliveryPoint').text
        self.city=elem.find('{http://www.opengis.net/ows}City').text
        self.administrativeArea=elem.find('{http://www.opengis.net/ows}AdministrativeArea').text
        self.postalCode=elem.find('{http://www.opengis.net/ows}PostalCode').text
        self.country=elem.find('{http://www.opengis.net/ows}Country').text
        self.electronicMailAddress=elem.find('{http://www.opengis.net/ows}ElectronicMailAddress').text
        self.email=self.electronicMailAddress #shorthand alias
        

class Phone(object):
    def __init__(self,elem):
        self.voice=elem.find('{http://www.opengis.net/ows}Voice').text
        self.facsimile=elem.find('{http://www.opengis.net/ows}Facsimile').text
        self.fax=self.facsimile #shorthand alias

class ContactInfo(object):
    def __init__(self,elem):
        #self.address=elem.find
        self.phone=Phone(elem.find('{http://www.opengis.net/ows}Phone'))
        self.address=Address(elem.find('{http://www.opengis.net/ows}Address'))
        
    
class ServiceContact(object):
    def __init__(self,elem):
        self.individualName=elem.find('{http://www.opengis.net/ows}IndividualName').text
        self.positionName=elem.find('{http://www.opengis.net/ows}PositionName').text
        contact=elem.find('{http://www.opengis.net/ows}ContactInfo')
        if contact is not None:
            self.contactInfo=ContactInfo(contact)
        else:
            self.contactInfo = None
        
  
class CoverageSummary(object):
    """Abstraction for WCS CoverageSummary
    """
    def __init__(self, elem, parent):
        """Initialize."""
        #TODO - examine the parent for bounding box info.
        
        self._elem=elem
        self._parent=parent
        self.identifier=self._checkChildAndParent('{http://www.opengis.net/wcs/1.1}Identifier')
        self.description =self._checkChildAndParent('{http://www.opengis.net/wcs/1.1}Description')           
        self.title =self._checkChildAndParent('{http://www.opengis.net/ows}Title')
        self.abstract =self._checkChildAndParent('{http://www.opengis.net/ows}Abstract')
        
        #keywords.
        self.keywords=[]
        for kw in elem.findall('{http://www.opengis.net/ows}Keywords/{http://www.opengis.net/ows}Keyword'):
            if kw is not None:
                self.keywords.append(kw.text)
        
        #also inherit any keywords from parent coverage summary (if there is one)
        if parent is not None:
            for kw in parent.findall('{http://www.opengis.net/ows}Keywords/{http://www.opengis.net/ows}Keyword'):
                if kw is not None:
                    self.keywords.append(kw.text)
            
        
        self.WGS84BoundingBox = None
        b = elem.find('{http://www.opengis.net/ows}WGS84BoundingBox')
        if b is not None:
            lc=b.find('{http://www.opengis.net/ows}LowerCorner').text
            uc=b.find('{http://www.opengis.net/ows}UpperCorner').text
            self.WGS84BoundingBox = (
                    float(lc.split()[0]),float(lc.split()[1]),
                    float(uc.split()[0]), float(uc.split()[1]),
                    )
                
        # bboxes - other CRS 
        self.boundingBoxes = []
        for bbox in elem.findall('{http://www.opengis.net/ows}BoundingBox'):
            if bbox is not None:
                lc=b.find('{http://www.opengis.net/ows}LowerCorner').text
                uc=b.find('{http://www.opengis.net/ows}UpperCorner').text
                boundingBox =  (
                        float(lc.split()[0]),float(lc.split()[1]),
                        float(uc.split()[0]), float(uc.split()[1]),
                        b.attrib['crs'])
                self.boundingBoxes.append(boundingBox)
        
        #SupportedCRS
        self.supportedCRS=[]
        for crs in elem.findall('{http://www.opengis.net/wcs/1.1}SupportedCRS'):
            self.supportedCRS.append(crs.text)
            
        #SupportedFormats         
        self.supportedFormats=[]
        for format in elem.findall('{http://www.opengis.net/wcs/1.1}SupportedFormat'):
            self.supportedFormats.append(format.text)
            
    def _checkChildAndParent(self, path):
        ''' checks child coverage  summary, and if item not found checks higher level coverage summary'''
        try:
            value = self._elem.find(path).text
        except:
            try:
                value = self._parent.find(path).text
            except:
                value = None
        return value  
            

class Capabilities(object):
    """Abstraction for WCS metadata.
    
    Implements ICapabilities.
    """
    def __init__(self, infoset):
        """Initialize from an element tree root element."""
        self._root = infoset
        #need to handle exception report
        #print infoset.tag
        #print infoset.text
        #serviceIdentification
        elem=self._root.find('{http://www.opengis.net/wcs/1.1/ows}ServiceIdentification')
        self.serviceIdentification=ServiceIdentification(elem)
        
        #serviceProvider
        elem=self._root.find('{http://www.opengis.net/ows}ServiceProvider')
        self.serviceProvider=ServiceProvider(elem)
        
        
        # operations []
        self.operations = []
        for elem in self._root.findall('{http://www.opengis.net/wcs/1.1/ows}OperationsMetadata/{http://www.opengis.net/wcs/1.1/ows}Operation/'):
            self.operations.append(OperationMetadata(elem))
        
        # exceptions - ***********TO DO *************
        self.exceptions = [f.text for f \
                in self._root.findall('Capability/Exception/Format')]
        
        # contents: our assumption is that services use a top-level layer
        # as a metadata organizer, nothing more.
        self.contents = []
        top = self._root.find('{http://www.opengis.net/wcs/1.1}Contents/{http://www.opengis.net/wcs/1.1}CoverageSummary')
        for elem in self._root.findall('{http://www.opengis.net/wcs/1.1}Contents/{http://www.opengis.net/wcs/1.1}CoverageSummary/{http://www.opengis.net/wcs/1.1}CoverageSummary'):                    
            self.contents.append(CoverageSummary(elem, top))
        if self.contents==[]:
            #non-hierarchical.
            top=None
            for elem in self._root.findall('{http://www.opengis.net/wcs/1.1}Contents/{http://www.opengis.net/wcs/1.1}CoverageSummary'):     
                self.contents.append(CoverageSummary(elem, top))                             
                
        # contact person TODO
        #self.provider = ContactMetadata(self._root.find('Service/ContactInformation'))

    
    def getOperationByName(self, name):
        """Return a named operation item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name
