#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#           Angelos Tzotsos <tzotsos@gmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

""" ISO metadata parser """

from owslib.etree import etree
from owslib import util

# default variables

namespaces = {
    None : 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'gml32': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'srv': 'http://www.isotc211.org/2005/srv',
    'xlink': 'http://www.w3.org/1999/xlink'
}

class MD_Metadata(object):
    """ Process gmd:MD_Metadata """
    def __init__(self, md):

        if isinstance(md, etree._Element) is False:  # standalone document
            self.xml = etree.tostring(md.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(md)

        val = md.find(util.nspath('fileIdentifier', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath('language', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.language = util.testXMLValue(val)
        
        val = md.find(util.nspath('language', namespaces['gmd']) + '/' + util.nspath('LanguageCode', namespaces['gmd']))
        self.languagecode = util.testXMLValue(val)
        
        val = md.find(util.nspath('dateStamp', namespaces['gmd']) + '/' + util.nspath('Date', namespaces['gco']))
        self.datestamp = util.testXMLValue(val)

        self.charset = _testCodeListValue(md.find(util.nspath('characterSet/MD_CharacterSetCode', namespaces['gmd'])))
  
        self.hierarchy = _testCodeListValue(md.find(util.nspath('hierarchyLevel/MD_ScopeCode', namespaces['gmd'])))

        self.contact = []
        for i in md.findall(util.nspath('contact/CI_ResponsibleParty', namespaces['gmd'])):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        val = md.find(util.nspath('dateStamp', namespaces['gmd']) + '/' + util.nspath('DateTime', namespaces['gco']))
        self.datetimestamp = util.testXMLValue(val)
        
        val = md.find(util.nspath('metadataStandardName', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.stdname = util.testXMLValue(val)

        val = md.find(util.nspath('metadataStandardVersion', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.stdver = util.testXMLValue(val)

        val = md.find(util.nspath('referenceSystemInfo/MD_ReferenceSystem', namespaces['gmd']))
        if val is not None:
            self.referencesystem = MD_ReferenceSystem(val)
        else:
            self.referencesystem = None

        val = md.find(util.nspath('identificationInfo/MD_DataIdentification', namespaces['gmd']))
        val2 = md.find(util.nspath('identificationInfo', namespaces['gmd']) + '/' + util.nspath('SV_ServiceIdentification', namespaces['srv']))

        if val is not None:
            self.identification = MD_DataIdentification(val, 'dataset')
            self.serviceidentification = None
        elif val2 is not None:
            self.identification = MD_DataIdentification(val2, 'service')
            self.serviceidentification = SV_ServiceIdentification(val2)
        else:
            self.identification = None
            self.serviceidentification = None

        val = md.find(util.nspath('distributionInfo/MD_Distribution', namespaces['gmd']))
        if val is not None:
            self.distribution = MD_Distribution(val)
        else:
            self.distribution = None
        
        val = md.find(util.nspath('dataQualityInfo/DQ_DataQuality', namespaces['gmd']))
        if val is not None:
            self.dataquality = DQ_DataQuality(val)
        else:
            self.dataquality = None

class CI_ResponsibleParty(object):
    """ process CI_ResponsibleParty """
    def __init__(self, md):
        val = md.find(util.nspath('individualName', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath('organisationName', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.organization = util.testXMLValue(val)

        val = md.find(util.nspath('positionName', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.position = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/phone/CI_Telephone/voice', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.phone = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/phone/CI_Telephone/facsimile', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.fax = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/deliveryPoint', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.address = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/city', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.city = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/administrativeArea', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.region = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/postalCode', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.postcode = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/country', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.country = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/address/CI_Address/electronicMailAddress', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.email = util.testXMLValue(val)

        val = md.find(util.nspath('contactInfo/CI_Contact/onlineResource/CI_OnlineResource', namespaces['gmd']))
        if val is not None:
          self.onlineresource = CI_OnlineResource(val)
        else:
          self.onlineresource = None
      
        self.role = _testCodeListValue(md.find(util.nspath('role/CI_RoleCode', namespaces['gmd'])))

class MD_DataIdentification(object):
    """ process MD_DataIdentification """
    def __init__(self, md, identtype):
        self.identtype = identtype
        val = md.find(util.nspath('citation/CI_Citation/title', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.title = util.testXMLValue(val)
        
        self.date = []
        self.datetype = []
        
        for i in md.findall(util.nspath('citation/CI_Citation/date', namespaces['gmd'])):
            k = i.find(util.nspath('CI_Date/date',  namespaces['gmd']) + '/' + util.nspath('DateTime', namespaces['gco']))
            k1 = util.testXMLValue(k)
            if k1 is not None:
                self.date.append(k1)
            
            k = i.find(util.nspath('CI_Date/dateType/CI_DateTypeCode',  namespaces['gmd']))
            k1 = util.testXMLValue(k)
            if k1 is not None:
                self.datetype.append(k1)
        
        self.uselimitation = []
        for i in md.findall(util.nspath('resourceConstraints/MD_Constraints/useLimitation',  namespaces['gmd']) + '/' + util.nspath('CharacterString',  namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.uselimitation.append(val)
        
        self.accessconstraints = []
        for i in md.findall(util.nspath('resourceConstraints/MD_LegalConstraints/accessConstraints/MD_RestrictionCode',  namespaces['gmd'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.accessconstraints.append(val)
        
        self.classification = []
        for i in md.findall(util.nspath('resourceConstraints/MD_LegalConstraints/accessConstraints/MD_ClassificationCode',  namespaces['gmd'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.classification.append(val)
        
        self.otherconstraints = []
        for i in md.findall(util.nspath('resourceConstraints/MD_LegalConstraints/otherConstraints',  namespaces['gmd']) + '/' + util.nspath('CharacterString',  namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.otherconstraints.append(val)
        
        self.denominators = []
        for i in md.findall(util.nspath('spatialResolution/MD_Resolution/equivalentScale/MD_RepresentativeFraction/denominator',  namespaces['gmd']) + '/' + util.nspath('Integer',  namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.denominators.append(val)
        
        self.distance = []
        self.uom = []
        for i in md.findall(util.nspath('spatialResolution/MD_Resolution/distance',  namespaces['gmd']) + '/' + util.nspath('Distance',  namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.distance.append(val)
            self.uom.append(i.get("uom"))
        
        self.resourcelanguage = []
        for i in md.findall(util.nspath('language/LanguageCode',  namespaces['gmd'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.resourcelanguage.append(val)
        
        val = md.find(util.nspath('edition', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.edition = util.testXMLValue(val)

        val = md.find(util.nspath('abstract', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.abstract = util.testXMLValue(val)

        val = md.find(util.nspath('purpose', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.purpose = util.testXMLValue(val, True)

        self.status = _testCodeListValue(md.find(util.nspath('status/MD_ProgressCode', namespaces['gmd'])))

        self.contact = []
        for i in md.findall(util.nspath('pointOfContact/CI_ResponsibleParty', namespaces['gmd'])):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        self.keywords = {}

        self.keywords['type'] = _testCodeListValue(md.find(util.nspath('descriptiveKeywords/MD_Keywords/type/MD_KeywordTypeCode', namespaces['gmd'])))

        self.keywords['list'] = [] 
        self.keywords['thesaurustitle'] = []
        self.keywords['thesaurusdate'] = []
        self.keywords['thesaurusdatetype'] = []
        for i in md.findall(util.nspath('descriptiveKeywords/MD_Keywords', namespaces['gmd'])):
            k = i.find(util.nspath('keyword', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
            self.keywords['list'].append(util.testXMLValue(k))
            k1 = i.find(util.nspath('thesaurusName/CI_Citation/title', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
            k2 = util.testXMLValue(k1)
            if k2 is not None:
                self.keywords['thesaurustitle'].append(k2)
            k1 = i.find(util.nspath('thesaurusName/CI_Citation/date/CI_Date/date', namespaces['gmd']) + '/' + util.nspath('Date', namespaces['gco']))
            k2 = util.testXMLValue(k1)
            if k2 is not None:
                self.keywords['thesaurusdate'].append(k2)
            k1 = i.find(util.nspath('thesaurusName/CI_Citation/date/CI_Date/dateType/CI_DateTypeCode', namespaces['gmd']))
            k2 = util.testXMLValue(k1)
            if k2 is not None:
                self.keywords['thesaurusdatetype'].append(k2)

        
        self.topiccategory = []
        for i in md.findall(util.nspath('topicCategory/MD_TopicCategoryCode',  namespaces['gmd'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.topiccategory.append(val)
        
        val = md.find(util.nspath('supplementalInformation', namespaces['gmd'])+ '/' + util.nspath('CharacterString', namespaces['gco']))
        self.supplementalinformation = util.testXMLValue(val)
        
        val = md.find(util.nspath('extent/EX_Extent/geographicElement', namespaces['gmd']))

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None
        
        self.temporalextent_start = []
        for i in md.findall(util.nspath('extent/EX_Extent/temporalElement/EX_TemporalExtent/extent',  namespaces['gmd']) + '/' + util.nspath('TimePeriod/beginPosition',  namespaces['gml'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.temporalextent_start.append(val)
        
        self.temporalextent_end = []
        for i in md.findall(util.nspath('extent/EX_Extent/temporalElement/EX_TemporalExtent/extent',  namespaces['gmd']) + '/' + util.nspath('TimePeriod/endPosition',  namespaces['gml'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.temporalextent_end.append(val)
        
        
class MD_Distribution(object):
    """ process MD_Distribution """
    def __init__(self, md):
        val = md.find(util.nspath('distributionFormat/MD_Format/name', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath('distributionFormat/MD_Format/version', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.version = util.testXMLValue(val)

        self.online = []

        for ol in md.findall(util.nspath('transferOptions/MD_DigitalTransferOptions/onLine/CI_OnlineResource', namespaces['gmd'])):
            self.online.append(CI_OnlineResource(ol))
        
class DQ_DataQuality(object):
    ''' process DQ_DataQuality'''
    def __init__(self, md):
        
        self.conformancetitle = []
        for i in md.findall(util.nspath('report/DQ_DomainConsistency/result/DQ_ConformanceResult/specification/CI_Citation/title', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancetitle.append(val)
        
        self.conformancedate = []
        for i in md.findall(util.nspath('report/DQ_DomainConsistency/result/DQ_ConformanceResult/specification/CI_Citation/date/CI_Date/date', namespaces['gmd']) + '/' + util.nspath('Date', namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedate.append(val)
        
        self.conformancedatetype = []
        for i in md.findall(util.nspath('report/DQ_DomainConsistency/result/DQ_ConformanceResult/specification/CI_Citation/date/CI_Date/dateType/CI_DateTypeCode', namespaces['gmd'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedatetype.append(val)
        
        self.conformancedegree = []
        for i in md.findall(util.nspath('report/DQ_DomainConsistency/result/DQ_ConformanceResult/pass', namespaces['gmd']) + '/' + util.nspath('Boolean', namespaces['gco'])):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedegree.append(val)
        
        val = md.find(util.nspath('lineage/LI_Lineage/statement', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.lineage = util.testXMLValue(val)

class SV_ServiceIdentification(object):
    """ process SV_ServiceIdentification """
    def __init__(self, md):
        val = md.find(util.nspath('serviceType', namespaces['srv']) + '/' + util.nspath('LocalName', namespaces['gco']))
        self.type = util.testXMLValue(val)
      
        val = md.find(util.nspath('serviceTypeVersion', namespaces['srv']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.version = util.testXMLValue(val)

        val = md.find(util.nspath('accessProperties', namespaces['srv']) + '/' + util.nspath('MD_StandardOrderProcess/fees', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.fees = util.testXMLValue(val)

        val = md.find(util.nspath('extent', namespaces['srv']) + '/' + util.nspath('EX_Extent', namespaces['gmd']))

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None

        self.couplingtype = _testCodeListValue(md.find(util.nspath('couplingType/SV_CouplingType', namespaces['gmd'])))

        self.operations = []

        for i in md.findall(util.nspath('containsOperations', namespaces['srv'])):
            tmp = {}
            val = i.find(util.nspath('SV_OperationMetadata/operationName', namespaces['srv']) + '/' + util.nspath('CharacterString', namespaces['gco']))
            tmp['name'] = util.testXMLValue(val)
            tmp['dcplist'] = []
            for d in i.findall(util.nspath('SV_OperationMetadata/DCP', namespaces['srv'])):
                tmp2 = _testCodeListValue(d.find(util.nspath('DCPList', namespaces['srv'])))
                tmp['dcplist'].append(tmp2)
         
            tmp['connectpoint'] = []
 
            for d in i.findall(util.nspath('SV_OperationMetadata/connectPoint', namespaces['srv'])):
                tmp3 = d.find(util.nspath('CI_OnlineResource', namespaces['gmd']))
                tmp['connectpoint'].append(CI_OnlineResource(tmp3))
            self.operations.append(tmp)

        self.operateson = []
         
        for i in md.findall(util.nspath('operatesOn', namespaces['srv'])):
            tmp = {}
            tmp['uuidref'] = i.attrib.get('uuidref')
            tmp['href'] = i.attrib.get(util.nspath('href', namespaces['xlink']))
            tmp['title'] = i.attrib.get(util.nspath('title', namespaces['xlink']))
            self.operateson.append(tmp)

class CI_OnlineResource(object):
    """ process CI_OnlineResource """
    def __init__(self,md):
        val = md.find(util.nspath('linkage/URL', namespaces['gmd']))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath('protocol', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.protocol = util.testXMLValue(val)

        val = md.find(util.nspath('name', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath('description', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.description = util.testXMLValue(val)

        self.function = _testCodeListValue(md.find(util.nspath('function/CI_OnLineFunctionCode', namespaces['gmd'])))

class EX_Extent(object):
    """ process EX_Extent """
    def __init__(self, md):
        val = md.find(util.nspath('EX_GeographicBoundingBox/westBoundLongitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.minx = util.testXMLValue(val)
        val = md.find(util.nspath('EX_GeographicBoundingBox/eastBoundLongitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.maxx = util.testXMLValue(val)
        val = md.find(util.nspath('EX_GeographicBoundingBox/southBoundLatitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.miny = util.testXMLValue(val)
        val = md.find(util.nspath('EX_GeographicBoundingBox/northBoundLatitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.maxy = util.testXMLValue(val)

        val = md.find(util.nspath('EX_GeographicDescription/geographicIdentifier/MD_Identifier/code', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.description_code = util.testXMLValue(val)

class MD_ReferenceSystem(object):
    """ process MD_ReferenceSystem """
    def __init__(self, md):
        val = md.find(util.nspath('referenceSystemIdentifier/RS_Identifier/code', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.code = util.testXMLValue(val)

def _testCodeListValue(elpath):
    if elpath is not None:
        return util.testXMLValue(elpath.attrib.get('codeListValue'), True)
    else:
        return None

class CodelistCatalogue(object):
    """ process CT_CodelistCatalogue """
    def __init__(self, ct):
        val = ct.find(util.nspath('name', namespaces['gmx']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.name = util.testXMLValue(val)
        val = ct.find(util.nspath('scope', namespaces['gmx']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.scope = util.testXMLValue(val)
        val = ct.find(util.nspath('fieldOfApplication', namespaces['gmx']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.fieldapp = util.testXMLValue(val)
        val = ct.find(util.nspath('versionNumber', namespaces['gmx']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.version = util.testXMLValue(val)
        val = ct.find(util.nspath('versionDate', namespaces['gmx']) + '/' + util.nspath('Date', namespaces['gco']))
        self.date = util.testXMLValue(val)

        self.dictionaries = {}

        for i in ct.findall(util.nspath('codelistItem/CodeListDictionary', namespaces['gmx'])):
            id = i.attrib.get(util.nspath('id', namespaces['gml']))
            self.dictionaries[id] = {}
            val = i.find(util.nspath('description', namespaces['gml']))
            self.dictionaries[id]['description'] = util.testXMLValue(val)
            val = i.find(util.nspath('identifier', namespaces['gml']))
            self.dictionaries[id]['identifier'] = util.testXMLValue(val)
            self.dictionaries[id]['entries'] = {}

            for j in i.findall(util.nspath('codeEntry', namespaces['gmx'])):
                id2 = j.find(util.nspath('CodeDefinition', namespaces['gmx'])).attrib.get(util.nspath('id', namespaces['gml']))
                self.dictionaries[id]['entries'][id2] = {}
                val = j.find(util.nspath('CodeDefinition', namespaces['gmx'])+'/'+util.nspath('description', namespaces['gml']))
                self.dictionaries[id]['entries'][id2]['description'] = util.testXMLValue(val)

                val = j.find(util.nspath('CodeDefinition', namespaces['gmx'])+'/'+util.nspath('identifier', namespaces['gml']))
                self.dictionaries[id]['entries'][id2]['identifier'] = util.testXMLValue(val)

                val = j.find(util.nspath('CodeDefinition', namespaces['gmx'])).attrib.get('codeSpace')
                self.dictionaries[id]['entries'][id2]['codespace'] = util.testXMLValue(val, True)

    def getcodelistdictionaries(self):
        return self.dictionaries.keys()

    def getcodedefinitionidentifiers(self, cdl):
        if self.dictionaries.has_key(cdl):
            ids = []
            for i in self.dictionaries[cdl]['entries']:
                ids.append(self.dictionaries[cdl]['entries'][i]['identifier'])
            return ids
        else:
            return None
