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

#  function to save writing out WCS namespace in full each time
def ns(tag):
    return '{http://www.opengis.net/wcs}'+tag

class ServiceException(Exception):
    pass


class WebCoverageService_1_0_0(WCSBase):
    """Abstraction for OGC Web Coverage Service (WCS), version 1.0.0
    Implements IWebCoverageService.
    """
    def __getitem__(self,name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if 'servicecontents' in self.__dict__.keys():
            if name in self.__getattribute__('servicecontents').keys():
                return self.__getattribute__('servicecontents')[name]
        #otherwise behave normally:
        return self.__getattribute__(self,name)
    
    def __init__(self,url,xml):
        self.version='1.0.0'
        self.url = url   
        self._capabilities = None
        # initialize from saved capability document or access the server
        reader = WCSCapabilitiesReader(self.version)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url)
        
        #get service type
        #self.service = self._capabilities.find(ns('Service/') + ns('name')).text
        #self.version='1.0.0'
        #self.url = url        

        #serviceIdentification metadata
        self.serviceidentification =None
        subelem=self._capabilities.find(ns('Service/'))
        self.serviceidentification=ServiceIdenfication(subelem)                               
                   
        #serviceProvider metadata
        self.serviceprovider =None
        subelem=self._capabilities.find(ns('Service/')+ns('responsibleParty'))
        self.serviceprovider=ServiceProvider(subelem)   
        
        #serviceOperations metadata
        self.serviceoperations=[]
        for elem in self._capabilities.find(ns('Capability/')+ns('Request')).getchildren():
            self.serviceoperations.append(OperationMetadata(elem))
          
        #serviceContents metadata
        self.servicecontents={}
        for elem in self._capabilities.findall(ns('ContentMetadata/')+ns('CoverageOfferingBrief')):
            cm=ContentMetadata(elem)
            self.servicecontents[cm.id]=cm
        
                # exceptions - ***********TO DO *************
        self.exceptions = [f.text for f \
                in self._capabilities.findall('Capability/Exception/Format')]
    
    
    def items(self):
        '''supports dict-like items() access'''
        items=[]
        for item in self.servicecontents:
            items.append((item,self.servicecontents[item]))
        return items
        
    #def _getaddressString(self):
        ##todo   
        #addobj=self.capabilities.service.responsibleParty.serviceContact.address
        #address=addobj.deliveryPoint + ',' + addobj.city +  ',' + addobj.administrativeArea +  ',' + addobj.postalCode +  ',' +  addobj.country
        #return address
        
  
    def getCoverage(self, identifier=None, bbox=None, timeSequence=None, format = None,  method='Get',**kwargs):
        """Request and return a coverage from the WCS as a file-like object
        note: additional **kwargs helps with multi-version implementation
        core keyword arguments should be supported cross version
        example:
        cvg=wcs.getCoverageRequest(identifier=['TuMYrRQ4'], timeSequence=['2792-06-01T00:00:00.0'], bbox=(-112,36,-106,41),format='application/netcdf')

        is equivalent to:
        http://myhost/mywcs?SERVICE=WCS&REQUEST=GetCoverage&IDENTIFIER=TuMYrRQ4&VERSION=1.1.0&BOUNDINGBOX=-180,-90,180,90&TIMESEQUENCE=[bb&FORMAT=application/netcdf
           

        """
        #use fully qualified namespace
        md = self.capabilities
        base_url = md.getOperationByName('GetCoverage').methods[method]['url']


        #process kwargs
        request = {'version': self.version, 'request': 'GetCoverage', 'service':'WCS'}
        assert len(identifier) > 0
        request['Coverage']=identifier
        #request['identifier'] = ','.join(identifier)
        if bbox:
            request['BBox']=','.join([str(x) for x in bbox])
        else:
            request['BBox']=None
        if timeSequence:
            request['timesequence']=','.join(timeSequence)
        else:
            request['timesequence']=None
        request['format']=format
        
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
    """Abstraction for WCS metadata.   
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag.split('}')[1]
        # formatOptions
             
        
        #self.formatOptions = [f.text for f in elem.findall('{http://www.opengis.net/wcs/1.1/ows}Parameter/{http://www.opengis.net/wcs/1.1/ows}AllowedValues/{http://www.opengis.net/wcs/1.1/ows}Value')]
        methods = []
        for resource in elem.findall(ns('DCPType/')+ns('HTTP/')+ns('Get/')+ns('OnlineResource')):
            url = resource.attrib['{http://www.w3.org/1999/xlink}href']
            methods.append(('Get', {'url': url}))        
        for resource in elem.findall(ns('DCPType/')+ns('HTTP/')+ns('Post/')+ns('OnlineResource')):
            url = resource.attrib['{http://www.w3.org/1999/xlink}href']
            methods.append(('Post', {'url': url}))        
        self.methods = dict(methods)
            
class ServiceIdenfication(object):
    """ Abstraction for ServiceIdentification metadata """
    def __init__(self,elem):
        # properties              
        self.service = elem.find(ns('name')).text
        try:
            self.abstract = elem.find(ns('description')).text
        except:
            self.abstract=None
        self.title = elem.find(ns('name')).text     
        self.keywords = [f.text for f in elem.findall(ns('keywords')+'/'+ns('keyword'))]
        #note: differs from 'rights' in interface
        self.fees=elem.find(ns('fees')).text
        self.accessConstraints=elem.find(ns('accessConstraints')).text
       
class ServiceProvider(object):
    """ Abstraction for WCS ResponsibleParty 
    Implements IServiceProvider"""
    def __init__(self,elem):
        self.provider=elem.find(ns('organisationName')).text
        try:
            self.provider=elem.find(ns('organisationName')).text
        except AttributeError: 
            self.provider=''
        self.url ="URL for provider's web site (string)."
        self.contact = "How to contact the service provider (string)."

#may not keep these contact info classes
class Address(object):
    def __init__(self,elem):
        try:
            self.deliveryPoint=elem.find(ns('deliveryPoint')).text
        except AttributeError:
            self.deliveryPoint=''
        try:
            self.city=elem.find(ns('city')).text
        except AttributeError:
            self. city=''       
        try:
            self.administrativeArea=elem.find(ns('administrativeArea')).text
        except AttributeError:
            self.administrativeArea=''
        try:
            self.postalCode=elem.find(ns('postalCode')).text
        except AttributeError:
            self.postalCode=''
        try:
            self.country=elem.find(ns('country')).text
        except AttributeError:
            self.country=''
        try:
            self.electronicMailAddress=elem.find(ns('electronicMailAddress')).text
        except AttributeError:
            self.electronicMailAddress=''
        self.email=self.electronicMailAddress #shorthand alias

class Phone(object):
    def __init__(self,elem):
        try:
            self.voice=elem.find(ns('voice')).text
        except:
            self.voice=''
        try:    
            self.facsimile=elem.find(ns('facsimile')).text
            self.fax=self.facsimile #shorthand alias
        except:
            self.facsimile=''
            self.fax=''

class ContactInfo(object):
    def __init__(self,elem):
        #self.address=elem.find
        self.phone=Phone(elem.find(ns('phone')))
        self.address=Address(elem.find(ns('address')))


class ContentMetadata(object):
    """
    Implements IContentMetadata
    """
    def __init__(self, elem):
        """Initialize."""
        #TODO - examine the parent for bounding box info.
        
        #self._parent=parent
        self.id=elem.find(ns('name')).text
        self.label =elem.find(ns('label')).text
        self.title=self.label #alias to align with 1.1.0          
        
        #keywords.       
        self.keywords = [f.text for f in elem.findall(ns('keywords')+'/'+ns('keyword'))]
                    
        
        self.boundingBoxWGS84 = None
        self.timepositions=None
        b = elem.find(ns('lonLatEnvelope'))
        if b is not None:
            gmlpositions=b.findall('{http://www.opengis.net/gml}pos')
            timepositions=b.findall('{http://www.opengis.net/gml}timePosition')
            lc=gmlpositions[0].text
            uc=gmlpositions[1].text
            self.boundingBoxWGS84 = (
                    float(lc.split()[0]),float(lc.split()[1]),
                    float(uc.split()[0]), float(uc.split()[1]),
                    )
            if timepositions:
                self.timelimits=[timepositions[0].text,timepositions[1].text]
            else:
                self.timelimits=None
        ## bboxes - other CRS TODO
        #self.boundingBoxes = []
        #for bbox in elem.findall('{http://www.opengis.net/ows}BoundingBox'):
            #if bbox is not None:
                #lc=b.find('{http://www.opengis.net/ows}LowerCorner').text
                #uc=b.find('{http://www.opengis.net/ows}UpperCorner').text
                #boundingBox =  (
                        #float(lc.split()[0]),float(lc.split()[1]),
                        #float(uc.split()[0]), float(uc.split()[1]),
                        #b.attrib['crs'])
                #self.boundingBoxes.append(boundingBox)
        
        #SupportedCRS, SupportedFormats
        self.supportedCRS=[f.text for f in elem.findall(ns('SupportedCRS'))]
        self.supportedFormats=[f.text for f in elem.findall(ns('SupportedFormat'))]
            
               
