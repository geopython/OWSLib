# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2004, 2006 Sean C. Gillies
# Copyright (c) 2007 STFC <http://www.stfc.ac.uk>
#
# Authors :
#          Oliver Clements <olcl@pml.ac.uk>
#
# Contact email: olcl@pml.ac.uk
# =============================================================================

##########NOTE: Does not conform to new interfaces yet #################


from __future__ import (absolute_import, division, print_function)

from owslib.coverage.wcsBase import WCSBase, WCSCapabilitiesReader, ServiceException
from owslib.ows import OwsCommon, ServiceIdentification, ServiceProvider, OperationsMetadata

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from owslib.util import openURL, testXMLValue
from owslib.etree import etree
from owslib.crs import Crs
import os, errno
import dateutil.parser as parser
from datetime import timedelta
import logging
from owslib.util import log, datetime_from_ansi, datetime_from_iso

#  function to save writing out WCS namespace in full each time
def ns(tag):
    return '{http://www.opengis.net/ows/2.0}'+tag

def nsWCS2(tag):
    return '{http://www.opengis.net/wcs/2.0}'+tag

class WebCoverageService_2_0_0(WCSBase):
    """Abstraction for OGC Web Coverage Service (WCS), version 2.0.0
    Implements IWebCoverageService.
    """
    def __getitem__(self,name):
        ''' check contents dictionary to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self,url,xml, cookies):
        self.version='2.0.0'
        self.url = url
        self.cookies=cookies
        self.ows_common = OwsCommon(version='2.0.0')
        # initialize from saved capability document or access the server
        reader = WCSCapabilitiesReader(self.version, self.cookies)
        if xml:
            self._capabilities = reader.readString(xml)
        else:
            self._capabilities = reader.read(self.url)

        # check for exceptions
        se = self._capabilities.find('ServiceException')

        if se is not None:
            err_message = str(se.text).strip()
            raise ServiceException(err_message, xml)

        #serviceIdentification metadata
        subelem=self._capabilities.find(ns('ServiceIdentification'))
        self.identification=ServiceIdentification(subelem, namespace=self.ows_common.namespace)

        #serviceProvider metadata
        serviceproviderelem=self._capabilities.find(ns('ServiceProvider'))
        self.provider=ServiceProvider(serviceproviderelem, namespace=self.ows_common.namespace)

        #serviceOperations metadata
        self.operations=[]
        for elem in self._capabilities.find(ns('OperationsMetadata'))[:]:
            if elem.tag !=ns('ExtendedCapabilities'):
                self.operations.append(OperationsMetadata(elem, namespace=self.ows_common.namespace))

        #serviceContents metadata
        self.contents={}
        for elem in self._capabilities.findall(nsWCS2('Contents/')+nsWCS2('CoverageSummary')):
            cm=ContentMetadata(elem, self)
            self.contents[cm.id]=cm



        #exceptions
        self.exceptions = [f.text for f \
                in self._capabilities.findall('Capability/Exception/Format')]


    def items(self):
        '''supports dict-like items() access'''
        items=[]
        for item in self.contents:
            items.append((item,self.contents[item]))
        return items

    def __makeString(self,value):
        #using repr unconditionally breaks things in some circumstances if a value is already a string
        if type(value) is not str:
            sval=repr(value)
        else:
            sval = value
        return sval

    def getCoverage(self, identifier=None, bbox=None, time=None, format = None,  subsets=None,crs=None, width=None, height=None, resx=None, resy=None, resz=None,parameter=None,method='Get',**kwargs):
        """Request and return a coverage from the WCS as a file-like object
        note: additional **kwargs helps with multi-version implementation
        core keyword arguments should be supported cross version
        example:
        cvg=wcs.getCoverage(identifier=['TuMYrRQ4'], timeSequence=['2792-06-01T00:00:00.0'], bbox=(-112,36,-106,41),format='cf-netcdf')

        is equivalent to:
        http://myhost/mywcs?SERVICE=WCS&REQUEST=GetCoverage&IDENTIFIER=TuMYrRQ4&VERSION=1.1.0&BOUNDINGBOX=-180,-90,180,90&TIME=2792-06-01T00:00:00.0&FORMAT=cf-netcdf

        example 2.0.1 URL
        http://earthserver.pml.ac.uk/rasdaman/ows?&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage
        &COVERAGEID=V2_monthly_CCI_chlor_a_insitu_test&SUBSET=Lat(40,50)&SUBSET=Long(-10,0)&SUBSET=ansi(144883,145000)&FORMAT=application/netcdf

        cvg=wcs.getCoverage(identifier=['myID'], format='application/netcdf', subsets=[('axisName',min,max),('axisName',min,max),('axisName',min,max)])


        """
        if log.isEnabledFor(logging.DEBUG):
            log.debug('WCS 2.0.0 DEBUG: Parameters passed to GetCoverage: identifier=%s, bbox=%s, time=%s, format=%s, crs=%s, width=%s, height=%s, resx=%s, resy=%s, resz=%s, parameter=%s, method=%s, other_arguments=%s'%(identifier, bbox, time, format, crs, width, height, resx, resy, resz, parameter, method, str(kwargs)))

        try:
            base_url = next((m.get('url') for m in self.getOperationByName('GetCoverage').methods if m.get('type').lower() == method.lower()))
        except StopIteration:
            base_url = self.url

        if log.isEnabledFor(logging.DEBUG):
            log.debug('WCS 2.0.0 DEBUG: base url of server: %s'%base_url)

        request = {'version': self.version, 'request': 'GetCoverage', 'service':'WCS'}
        assert len(identifier) > 0
        request['CoverageID']=identifier[0]


        if crs:
            request['crs']=crs
        request['format']=format
        if width:
            request['width']=width
        if height:
            request['height']=height

        #anything else e.g. vendor specific parameters must go through kwargs
        if kwargs:
            for kw in kwargs:
                request[kw]=kwargs[kw]

        #encode and request
        data = urlencode(request)
        if subsets:
            for subset in subsets:
                if len(subset) > 2:
                    if not self.is_number(subset[1]):
                        data = data + "&"+ urlencode({"subset":subset[0]+'("'+self.__makeString(subset[1])+'","'+self.__makeString(subset[2])+'")'})
                    else:
                        data = data + "&"+ urlencode({"subset":subset[0]+'('+self.__makeString(subset[1])+','+self.__makeString(subset[2])+')'})
                else:
                    if not self.is_number(subset[1]):
                        data = data + "&"+ urlencode({"subset":subset[0]+'("'+self.__makeString(subset[1])+'")'})
                    else:
                        data = data + "&"+ urlencode({"subset":subset[0]+'('+self.__makeString(subset[1])+')'})


        if log.isEnabledFor(logging.DEBUG):
            log.debug('WCS 2.0.0 DEBUG: Second part of URL: %s'%data)

        u=openURL(base_url, data, method, self.cookies)

        return u

    def is_number(self,s):
        """simple helper to test if value is number as requests with numbers dont
        need quote marks
        """
        try:
            float(s)
            return True
        except ValueError:
            return False

    def getOperationByName(self, name):
        """Return a named operation item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)



class ContentMetadata(object):
    """
    Implements IContentMetadata
    """
    def __init__(self, elem, service):
        """Initialize. service is required so that describeCoverage requests may be made"""
        #TODO - examine the parent for bounding box info.
        self._elem=elem
        self._service=service
        self.id=elem.find(nsWCS2('CoverageId')).text
        self.title = testXMLValue(elem.find(ns('label')))
        self.abstract= testXMLValue(elem.find(ns('description')))
        self.keywords = [f.text for f in elem.findall(ns('keywords')+'/'+ns('keyword'))]
        self.boundingBox=None #needed for iContentMetadata harmonisation
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
        #others not used but needed for iContentMetadata harmonisation
        self.styles=None
        self.crsOptions=None
        self.defaulttimeposition=None

    #grid is either a gml:Grid or a gml:RectifiedGrid if supplied as part of the DescribeCoverage response.
    def _getGrid(self):
        if not hasattr(self, 'descCov'):
                self.descCov=self._service.getDescribeCoverage(self.id)
        gridelem= self.descCov.find(nsWCS2('CoverageDescription/')+'{http://www.opengis.net/gml/3.2}domainSet/'+'{http://www.opengis.net/gml/3.3/rgrid}ReferenceableGridByVectors')
        if gridelem is not None:
            grid=ReferenceableGridByVectors(gridelem)
        else:
            # HERE I LOOK FOR RECTIFIEDGRID
            gridelem=self.descCov.find(nsWCS2('CoverageDescription/')+'{http://www.opengis.net/gml/3.2}domainSet/'+'{http://www.opengis.net/gml/3.2}RectifiedGrid')
            grid=RectifiedGrid(gridelem)
        return grid
    grid=property(_getGrid, None)

     #timelimits are the start/end times, timepositions are all timepoints. WCS servers can declare one or both or neither of these.
     # in wcs 2.0 this can be gathered from the Envelope tag
    def _getTimeLimits(self):
        # timepoints, timelimits=[],[]
        # b=self._elem.find(ns('lonLatEnvelope'))
        # if b is not None:
        #     timepoints=b.findall('{http://www.opengis.net/gml}timePosition')
        # else:
        #     #have to make a describeCoverage request...
        #     if not hasattr(self, 'descCov'):
        #         self.descCov=self._service.getDescribeCoverage(self.id)
        #     for pos in self.descCov.findall(ns('CoverageOffering/')+ns('domainSet/')+ns('temporalDomain/')+'{http://www.opengis.net/gml}timePosition'):
        #         timepoints.append(pos)
        # if timepoints:
        #         timelimits=[timepoints[0].text,timepoints[1].text]
        return [self.timepositions[0],self.timepositions[-1]]
    timelimits=property(_getTimeLimits, None)

    def _getTimePositions(self):

        timepositions=[]
        if not hasattr(self, 'descCov'):
            self.descCov=self._service.getDescribeCoverage(self.id)

        gridelem= self.descCov.find(nsWCS2('CoverageDescription/')+'{http://www.opengis.net/gml/3.2}domainSet/'+'{http://www.opengis.net/gml/3.3/rgrid}ReferenceableGridByVectors')
        if gridelem is not None:
            # irregular time axis
            cooeficients = []

            grid_axes = gridelem.findall('{http://www.opengis.net/gml/3.3/rgrid}generalGridAxis')
            for elem in grid_axes:
                if elem.find('{http://www.opengis.net/gml/3.3/rgrid}GeneralGridAxis/{http://www.opengis.net/gml/3.3/rgrid}gridAxesSpanned').text in ["ansi", "unix"]:
                   cooeficients = elem.find('{http://www.opengis.net/gml/3.3/rgrid}GeneralGridAxis/{http://www.opengis.net/gml/3.3/rgrid}coefficients').text.split(' ')
            for x in cooeficients:
                x = x.replace('"', '')
                t_date = datetime_from_iso(x)
                timepositions.append(t_date)
        else:
            # regular time
            if(len(self.grid.origin)>2):
                t_grid = self.grid
                t_date = t_grid.origin[2]
                start_pos = parser.parse(t_date, fuzzy=True)
                step = float(t_grid.offsetvectors[2][2])
                
                start_pos = start_pos + timedelta(days=(step/2))
                no_steps = int(t_grid.highlimits[2])
                for x in range(no_steps):
                    t_pos = start_pos +  timedelta(days=(step * x))
                    #t_date = datetime_from_ansi(t_pos)
                    #t_date = t_pos.isoformat()
                    timepositions.append(t_pos)
            else:
                # no time axis
                timepositions = None

        return timepositions
    timepositions=property(_getTimePositions, None)


    def _getOtherBoundingBoxes(self):
        ''' incomplete, should return other bounding boxes not in WGS84
            #TODO: find any other bounding boxes. Need to check for gml:EnvelopeWithTimePeriod.'''

        bboxes=[]

        if not hasattr(self, 'descCov'):
            self.descCov=self._service.getDescribeCoverage(self.id)

        for envelope in self.descCov.findall(nsWCS2('CoverageDescription/')+'{http://www.opengis.net/gml/3.2}boundedBy/'+'{http://www.opengis.net/gml/3.2}Envelope'):
            bbox = {}
            bbox['nativeSrs'] = envelope.attrib['srsName']
            lc = envelope.find('{http://www.opengis.net/gml/3.2}lowerCorner')
            lc =lc.text.split()
            uc = envelope.find('{http://www.opengis.net/gml/3.2}upperCorner')
            uc =uc.text.split()
            bbox['bbox'] = (
                float(lc[0]),float(lc[1]),
                float(uc[0]), float(uc[1])
            )
            bboxes.append(bbox)

        return bboxes
    boundingboxes=property(_getOtherBoundingBoxes,None)

    def _getSupportedCRSProperty(self):
        # gets supported crs info
        crss=[]
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('responseCRSs')):
            for crs in elem.text.split(' '):
                crss.append(Crs(crs))
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('requestResponseCRSs')):
            for crs in elem.text.split(' '):
                crss.append(Crs(crs))
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('supportedCRSs/')+ns('nativeCRSs')):
            for crs in elem.text.split(' '):
                crss.append(Crs(crs))
        return crss
    supportedCRS=property(_getSupportedCRSProperty, None)


    def _getSupportedFormatsProperty(self):
        # gets supported formats info
        frmts =[]
        for elem in self._service._capabilities.findall(nsWCS2('ServiceMetadata/')+nsWCS2('formatSupported')):
            frmts.append(elem.text)
        return frmts
    supportedFormats=property(_getSupportedFormatsProperty, None)

    def _getAxisDescriptionsProperty(self):
        #gets any axis descriptions contained in the rangeset (requires a DescribeCoverage call to server).
        axisDescs =[]
        for elem in self._service.getDescribeCoverage(self.id).findall(ns('CoverageOffering/')+ns('rangeSet/')+ns('RangeSet/')+ns('axisDescription/')+ns('AxisDescription')):
            axisDescs.append(AxisDescription(elem)) #create a 'AxisDescription' object.
        return axisDescs
    axisDescriptions=property(_getAxisDescriptionsProperty, None)



#Adding classes to represent gml:grid and gml:rectifiedgrid. One of these is used for the cvg.grid property
#(where cvg is a member of the contents dictionary)
#There is no simple way to convert the offset values in a rectifiedgrid grid to real values without CRS understanding, therefore this is beyond the current scope of owslib, so the representation here is purely to provide access to the information in the GML.

class Grid(object):
    ''' Simple grid class to provide axis and value information for a gml grid '''
    def __init__(self, grid):
        self.axislabels = []
        self.dimension=None
        self.lowlimits=[]
        self.highlimits=[]

        if grid is not None:
            self.dimension=int(grid.get('dimension'))
            self.lowlimits= grid.find('{http://www.opengis.net/gml/3.2}limits/{http://www.opengis.net/gml/3.2}GridEnvelope/{http://www.opengis.net/gml/3.2}low').text.split(' ')
            self.highlimits = grid.find('{http://www.opengis.net/gml/3.2}limits/{http://www.opengis.net/gml/3.2}GridEnvelope/{http://www.opengis.net/gml/3.2}high').text.split(' ')
            for axis in grid.findall('{http://www.opengis.net/gml/3.2}axisLabels')[0].text.split(' '):
                self.axislabels.append(axis)


class RectifiedGrid(Grid):
    ''' RectifiedGrid class, extends Grid with additional offset vector information '''
    def __init__(self, rectifiedgrid):
        super(RectifiedGrid,self).__init__(rectifiedgrid)
        self.origin=rectifiedgrid.find('{http://www.opengis.net/gml/3.2}origin/{http://www.opengis.net/gml/3.2}Point/{http://www.opengis.net/gml/3.2}pos').text.split()
        self.offsetvectors=[]
        for offset in rectifiedgrid.findall('{http://www.opengis.net/gml/3.2}offsetVector'):
            self.offsetvectors.append(offset.text.split())


class ReferenceableGridByVectors(Grid):
    ''' ReferenceableGridByVectors class, extends Grid with additional vector information '''
    def __init__(self, refereceablegridbyvectors):
        super(ReferenceableGridByVectors,self).__init__(refereceablegridbyvectors)
        self.origin=refereceablegridbyvectors.find('{http://www.opengis.net/gml/3.3/rgrid}origin/{http://www.opengis.net/gml/3.2}Point/{http://www.opengis.net/gml/3.2}pos').text.split()
        self.offsetvectors=[]
        for offset in refereceablegridbyvectors.findall('{http://www.opengis.net/gml/3.3/rgrid}generalGridAxis/{http://www.opengis.net/gml/3.3/rgrid}GeneralGridAxis/{http://www.opengis.net/gml/3.3/rgrid}offsetVector'):
            self.offsetvectors.append(offset.text.split())

class AxisDescription(object):
    ''' Class to represent the AxisDescription element optionally found as part of the RangeSet and used to
    define ordinates of additional dimensions such as wavelength bands or pressure levels'''
    def __init__(self, axisdescElem):
        self.name=self.label=None
        self.values=[]
        for elem in axisdescElem.getchildren():
            if elem.tag == ns('name'):
                self.name = elem.text
            elif elem.tag == ns('label'):
                self.label = elem.text
            elif elem.tag == ns('values'):
                for child in elem.getchildren():
                    self.values.append(child.text)
