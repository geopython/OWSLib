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

from wcsBase import WCSBase, WCSCapabilitiesReader, RereadableURL
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
        return self.__getattribute__(name)
    
    def __init__(self,url,xml):
        self.version='1.0.0'
        self.url = url   
        # initialize from saved capability document or access the server
        reader = WCSCapabilitiesReader(self.version)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url)

        #serviceIdentification metadata
        subelem=self._capabilities.find(ns('Service/'))
        self.serviceidentification=ServiceIdenfication(subelem)                               
                   
        #serviceProvider metadata
        subelem=self._capabilities.find(ns('Service/')+ns('responsibleParty'))
        self.serviceprovider=ServiceProvider(subelem)   
        
        #serviceOperations metadata
        self.serviceoperations=[]
        for elem in self._capabilities.find(ns('Capability/')+ns('Request')).getchildren():
            self.serviceoperations.append(OperationMetadata(elem))
          
        #serviceContents metadata
        self.servicecontents={}
        for elem in self._capabilities.findall(ns('ContentMetadata/')+ns('CoverageOfferingBrief')): 
            cm=ContentMetadata(elem, self)
            self.servicecontents[cm.id]=cm
        
        #exceptions
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
        
  
    def getCoverage(self, identifier=None, bbox=None, time=None, format = None,  width=None, height=None, resx=None, resy=None, resz=None,parameter=None,method='Get',**kwargs):
        """Request and return a coverage from the WCS as a file-like object
        note: additional **kwargs helps with multi-version implementation
        core keyword arguments should be supported cross version
        example:
        cvg=wcs.getCoverage(identifier=['TuMYrRQ4'], timeSequence=['2792-06-01T00:00:00.0'], bbox=(-112,36,-106,41),format='cf-netcdf')

        is equivalent to:
        http://myhost/mywcs?SERVICE=WCS&REQUEST=GetCoverage&IDENTIFIER=TuMYrRQ4&VERSION=1.1.0&BOUNDINGBOX=-180,-90,180,90&TIMESEQUENCE=['2792-06-01T00:00:00.0']&FORMAT=cf-netcdf
           
        """
        #TODO: handle kwargs - they can be used for 'PARAMETER' type key value pairs.
        
        base_url = self._getOperationByName('GetCoverage').methods[method]['url']
        
        #process kwargs
        request = {'version': self.version, 'request': 'GetCoverage', 'service':'WCS'}
        assert len(identifier) > 0
        request['Coverage']=identifier
        #request['identifier'] = ','.join(identifier)
        if bbox:
            request['BBox']=','.join([str(x) for x in bbox])
        else:
            request['BBox']=None
        if time:
            request['time']=','.join(time)
        else:
            request['time']=None
        request['format']=format
        if width:
            request['width']=width
        if height:
            request['height']=height
        if resx:
            request['resx']=resx
        if resy:
            request['resy']=resy
        if resz:
            request['resz']=resz
        
        #anything else e.g. vendor specific parameters must go through kwargs
        if kwargs:
            for kw in kwargs:
                request[kw]=kwargs[kw]
        
        #encode and request
        data = urlencode(request)
        fullurl=base_url + '?' + data
        u=urlopen(fullurl)

        # check for service exceptions, and return #TODO - test this bit properly.
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
               
    def _getOperationByName(self, name):
        """Return a named operation item."""
        for item in self.serviceoperations:
            if item.name == name:
                return item
        raise KeyError, "No operation named %s" % name
    
class OperationMetadata(object):
    """Abstraction for WCS metadata.   
    Implements IMetadata.
    """
    def __init__(self, elem):
        """."""
        self.name = elem.tag.split('}')[1]          
        
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
        self.version='1.0.0'
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
        try:
            self.provider=elem.find(ns('organisationName')).text
        except AttributeError: 
            self.provider=''
        self.url ="URL for provider's web site (string)." #TODO
        self.contact = "How to contact the service provider (string)."  #TO DECIDE - simple attributes?
        

#TO DECIDE: may not keep these contact info classes
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


#TO DO:  Times can be supplied as begin & end time or series of times (or both... )
#reflect this in the api.
class ContentMetadata(object):
    """
    Implements IContentMetadata
    """
    def __init__(self, elem, service):
        """Initialize. service is required so that describeCoverage requests may be made"""
        #TODO - examine the parent for bounding box info.
        
        #self._parent=parent
        self._elem=elem
        self._service=service
        self.id=elem.find(ns('name')).text
        self.title =elem.find(ns('label')).text       
        self.keywords = [f.text for f in elem.findall(ns('keywords')+'/'+ns('keyword'))]
                    
        
        self.boundingBoxWGS84 = None
        b = elem.find(ns('lonLatEnvelope'))
        if b is not None:
            gmlpositions=b.findall('{http://www.opengis.net/gml}pos')
            lc=gmlpositions[0].text
            uc=gmlpositions[1].text
            self.boundingBoxWGS84 = (
                    float(lc.split()[0]),float(lc.split()[1]),
                    float(uc.split()[0]), float(uc.split()[1]),
                    )
            
    def _getTimeLimits(self):
        timelimits=[]
        b=self._elem.find(ns('lonLatEnvelope'))
        if b is not None:
            timepoints=b.findall('{http://www.opengis.net/gml}timePosition')
        else:
            #have to make a describeCoverage request...
            descCov=self._service.getDescribeCoverage(self.id)
            for pos in self._elem.findall(ns('CoverageOffering/')+ns('domainSet/')+ns('temporalDomain/')+'{http://www.opengis.net/gml}timePosition'):
                timepoints.append(pos)
        if timepoints:
                timelimits=[timepoints[0].text,timepoints[1].text]
        return timelimits
    timelimits=property(_getTimeLimits, None)   
    
    def _getTimePositions(self):
        #TODO
        return []
    timepositions=property(_getTimePositions, None)
           
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
        #these require a seperate describeCoverage request...      only resolve when requested
    
    def _getSupportedCRSProperty(self):
        # gets supported crs info
        crss=[]
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('responseCRSs')):
            for crs in elem.text.split(' '):
                crss.append(crs)
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('requestResponseCRSs')):
            for crs in elem.text.split(' '):
                crss.append(crs)
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('nativeCRSs')):
            for crs in elem.text.split(' '):
                crss.append(crs)
        return crss
    supportedCRS=property(_getSupportedCRSProperty, None)
       
       
    def _getSupportedFormatsProperty(self):
        # gets supported formats info
        frmts =[]
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedFormats/')+ns('formats')):
            frmts.append(elem.text)
        return frmts
    supportedFormats=property(_getSupportedFormatsProperty, None)
        
        
