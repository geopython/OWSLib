#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
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
    'gml': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
    'gts': 'http://www.isotc211.org/2005/gts',
    'srv': 'http://www.isotc211.org/2005/srv',
    'xlink': 'http://www.w3.org/1999/xlink'
}

class MD_Metadata(object):
    """ Process gmd:MD_Metadata """
    def __init__(self, md):
        val = md.find(util.nspath('fileIdentifier', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath('language', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.language = util.testXMLValue(val)

        self.charset = _testCodeListValue(md.find(util.nspath('characterSet/MD_CharacterSetCode', namespaces['gmd'])))
  
        self.hierarchy = _testCodeListValue(md.find(util.nspath('hierarchyLevel/MD_ScopeCode', namespaces['gmd'])))

        val = md.find(util.nspath('contact/CI_ResponsibleParty', namespaces['gmd']))
        if val is not None:
            self.contact = CI_ResponsibleParty(val)
        else:
            self.contact = None

        val = md.find(util.nspath('dateStamp', namespaces['gmd']) + '/' + util.nspath('DateTime', namespaces['gco']))
        self.datestamp = util.testXMLValue(val)
        
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
        elif val2 is not None:
            self.identification = MD_DataIdentification(val2, 'service')
            self.identification.service = SV_ServiceIdentification(val2)
        else:
            self.identification = None

        val = md.find(util.nspath('distributionInfo/MD_Distribution', namespaces['gmd']))
        if val is not None:
            self.distribution = MD_Distribution(val)
        else:
            self.distribution = None

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

        val = md.find(util.nspath('citation/CI_Citation/date/CI_Date/date', namespaces['gmd']) + '/' + util.nspath('DateTime', namespaces['gco']))
        self.date = util.testXMLValue(val)

        self.datetype = _testCodeListValue(md.find(util.nspath('citation/CI_Citation/date/CI_Date/dateType/CI_DateTypeCode', namespaces['gmd'])))

        val = md.find(util.nspath('edition', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.edition = util.testXMLValue(val)

        val = md.find(util.nspath('abstract', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.abstract = util.testXMLValue(val)

        val = md.find(util.nspath('purpose', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.purpose = util.testXMLValue(val, True)

        self.status = _testCodeListValue(md.find(util.nspath('status/MD_ProgressCode', namespaces['gmd'])))

        val = md.find(util.nspath('pointOfContact/CI_ResponsibleParty', namespaces['gmd']))

        if val is not None:
            self.contact = CI_ResponsibleParty(val)
        else:
            self.contact = None

        self.keywords = {}

        self.keywords['type'] = _testCodeListValue(md.find(util.nspath('descriptiveKeywords/MD_Keywords/type/MD_KeywordTypeCode', namespaces['gmd'])))

        self.keywords['list'] = [] 
        for i in md.findall(util.nspath('descriptiveKeywords/MD_Keywords/keyword', namespaces['gmd'])):
            k = i.find(util.nspath('CharacterString', namespaces['gco']))
            self.keywords['list'].append(util.testXMLValue(k))

        val = md.find(util.nspath('topicCategory/MD_TopicCategoryCode', namespaces['gmd']))
        self.topiccategory = util.testXMLValue(val)

        val = md.find(util.nspath('extent/EX_Extent', namespaces['gmd']))

        val = md.find(util.nspath('supplementalInformation', namespaces['gmd'])+ '/' + util.nspath('CharacterString', namespaces['gco']))
        self.supplementalinformation = util.testXMLValue(val)

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None
        
class MD_Distribution(object):
    """ process MD_Distribution """
    def __init__(self, md):
        val = md.find(util.nspath('distributionFormat/MD_Format/name', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath('distributionFormat/MD_Format/version', namespaces['gmd']) + '/' + util.nspath('CharacterString', namespaces['gco']))
        self.version = util.testXMLValue(val)

        val = md.find(util.nspath('transferOptions/MD_DigitalTransferOptions/onLine/CI_OnlineResource', namespaces['gmd']))

        if val is not None:
            self.onlineresource = CI_OnlineResource(val)
        else:
            self.onlineresource = None
        
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
        val = md.find(util.nspath('geographicElement/EX_GeographicBoundingBox/westBoundLongitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.minx = util.testXMLValue(val)
        val = md.find(util.nspath('geographicElement/EX_GeographicBoundingBox/eastBoundLongitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.maxx = util.testXMLValue(val)
        val = md.find(util.nspath('geographicElement/EX_GeographicBoundingBox/southBoundLatitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.miny = util.testXMLValue(val)
        val = md.find(util.nspath('geographicElement/EX_GeographicBoundingBox/northBoundLatitude', namespaces['gmd']) + '/' + util.nspath('Decimal', namespaces['gco']))
        self.maxy = util.testXMLValue(val)

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
