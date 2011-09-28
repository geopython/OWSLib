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

        if hasattr(md, 'getroot'):  # standalone document
            self.xml = etree.tostring(md.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(md)

        val = md.find(util.nspath_eval('gmd:fileIdentifier/gco:CharacterString', namespaces))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:parentIdentifier/gco:CharacterString', namespaces))
        self.parentidentifier = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:language/gco:CharacterString', namespaces))
        self.language = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:datasetURI/gco:CharacterString', namespaces))
        self.dataseturi = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces))
        self.languagecode = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:dateStamp/gco:Date', namespaces))
        self.datestamp = util.testXMLValue(val)

        self.charset = _testCodeListValue(md.find(util.nspath_eval('gmd:characterSet/gmd:MD_CharacterSetCode', namespaces)))
  
        self.hierarchy = _testCodeListValue(md.find(util.nspath_eval('gmd:hierarchyLevel/gmd:MD_ScopeCode', namespaces)))

        self.contact = []
        for i in md.findall(util.nspath_eval('gmd:contact/gmd:CI_ResponsibleParty', namespaces)):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        val = md.find(util.nspath_eval('gmd:dateStamp/gco:DateTime', namespaces))
        self.datetimestamp = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:metadataStandardName/gco:CharacterString', namespaces))
        self.stdname = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:metadataStandardVersion/gco:CharacterString', namespaces))
        self.stdver = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:referenceSystemInfo/gmd:MD_ReferenceSystem', namespaces))
        if val is not None:
            self.referencesystem = MD_ReferenceSystem(val)
        else:
            self.referencesystem = None

        val = md.find(util.nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification', namespaces))
        val2 = md.find(util.nspath_eval('gmd:identificationInfo/srv:SV_ServiceIdentification', namespaces))

        if val is not None:
            self.identification = MD_DataIdentification(val, 'dataset')
            self.serviceidentification = None
        elif val2 is not None:
            self.identification = MD_DataIdentification(val2, 'service')
            self.serviceidentification = SV_ServiceIdentification(val2)
        else:
            self.identification = None
            self.serviceidentification = None

        val = md.find(util.nspath_eval('gmd:distributionInfo/gmd:MD_Distribution', namespaces))
        if val is not None:
            self.distribution = MD_Distribution(val)
        else:
            self.distribution = None
        
        val = md.find(util.nspath_eval('gmd:dataQualityInfo/gmd:DQ_DataQuality', namespaces))
        if val is not None:
            self.dataquality = DQ_DataQuality(val)
        else:
            self.dataquality = None

class CI_Date(object):
    """ process CI_Date """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:date/gco:Date', namespaces))
        if val is not None:
            self.date = util.testXMLValue(val)
        else:
            val = md.find(util.nspath_eval('gmd:date/gco:DateTime', namespaces))
            if val is not None:
                self.date = util.testXMLValue(val)
            else:
                self.date = None

        val = md.find(util.nspath_eval('gmd:dateType/gmd:CI_DateTypeCode', namespaces))
        if val is not None:
            self.type = util.testXMLValue(val)
        else:
            self.type = util.testXMLValue(md.attrib.get('codeListValue'), True)

class CI_ResponsibleParty(object):
    """ process CI_ResponsibleParty """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:individualName/gco:CharacterString', namespaces))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:organisationName/gco:CharacterString', namespaces))
        self.organization = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:positionName/gco:CharacterString', namespaces))
        self.position = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString', namespaces))

        self.phone = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString', namespaces))
        self.fax = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString', namespaces))
        self.address = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString', namespaces))
        self.city = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString', namespaces))
        self.region = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString', namespaces))
        self.postcode = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString', namespaces))
        self.country = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString', namespaces))
        self.email = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource', namespaces))
        if val is not None:
          self.onlineresource = CI_OnlineResource(val)
        else:
          self.onlineresource = None
      
        self.role = _testCodeListValue(md.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode', namespaces)))

class MD_DataIdentification(object):
    """ process MD_DataIdentification """
    def __init__(self, md, identtype):
        self.identtype = identtype
        val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
        self.title = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString', namespaces))
        self.alternatetitle = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:aggregationInfo', namespaces))
        self.aggregationinfo = util.testXMLValue(val)

        self.date = []
        self.datetype = []
        
        for i in md.findall(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date', namespaces)):
            self.date.append(CI_Date(i))
        
        self.uselimitation = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.uselimitation.append(val)
        
        self.accessconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.accessconstraints.append(val)
        
        self.classification = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_ClassificationCode', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.classification.append(val)
        
        self.otherconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.otherconstraints.append(val)

        self.securityconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:useLimitation', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.securityconstraints.append(val)
        
        self.denominators = []
        for i in md.findall(util.nspath_eval('gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.denominators.append(val)
        
        self.distance = []
        self.uom = []
        for i in md.findall(util.nspath_eval('gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.distance.append(val)
            self.uom.append(i.get("uom"))
        
        self.resourcelanguage = []
        for i in md.findall(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.resourcelanguage.append(val)

        val = md.find(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:organisationName', namespaces))
        if val is not None:
            val2 = val.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode', namespaces)) 
            if val2 is not None:
                clv = _testCodeListValue(val)
                if clv == 'originator':
                    self.creator = util.testXMLValue(val)
                elif clv == 'publisher':
                    self.publisher = util.testXMLValue(val)
                elif clv == 'contributor':
                    self.originator = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:edition/gco:CharacterString', namespaces))
        self.edition = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:abstract/gco:CharacterString', namespaces))
        self.abstract = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:purpose/gco:CharacterString', namespaces))
        self.purpose = util.testXMLValue(val, True)

        self.status = _testCodeListValue(md.find(util.nspath_eval('gmd:status/gmd:MD_ProgressCode', namespaces)))

        self.contact = []
        for i in md.findall(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty', namespaces)):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        self.keywords = []

        for i in md.findall(util.nspath_eval('gmd:descriptiveKeywords', namespaces)):
            mdkw = {}
            mdkw['type'] = _testCodeListValue(i.find(util.nspath_eval('gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode', namespaces)))

            mdkw['thesaurus'] = {}

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
            mdkw['thesaurus']['title'] = util.testXMLValue(val)

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date', namespaces))
            mdkw['thesaurus']['date'] = util.testXMLValue(val)

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode', namespaces))
            mdkw['thesaurus']['datetype'] = util.testXMLValue(val)

            mdkw['keywords'] = []

            for k in i.findall(util.nspath_eval('gmd:MD_Keywords/gmd:keyword', namespaces)):
                val = k.find(util.nspath_eval('gco:CharacterString', namespaces))
                mdkw['keywords'].append(util.testXMLValue(val))

            self.keywords.append(mdkw)
        
        self.topiccategory = []
        for i in md.findall(util.nspath_eval('gmd:topicCategory/gmd:MD_TopicCategoryCode', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.topiccategory.append(val)
        
        val = md.find(util.nspath_eval('gmd:supplementalInformation/gco:CharacterString', namespaces))
        self.supplementalinformation = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:geographicElement', namespaces))

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None
        
        val = md.find(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition', namespaces))
        self.temporalextent_start = util.testXMLValue(val)
        
        self.temporalextent_end = []
        val = md.find(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition', namespaces))
        self.temporalextent_end = util.testXMLValue(val)
        
class MD_Distribution(object):
    """ process MD_Distribution """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString', namespaces))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString', namespaces))
        self.version = util.testXMLValue(val)

        self.online = []

        for ol in md.findall(util.nspath_eval('gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource', namespaces)):
            self.online.append(CI_OnlineResource(ol))
        
class DQ_DataQuality(object):
    ''' process DQ_DataQuality'''
    def __init__(self, md):
        
        self.conformancetitle = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancetitle.append(val)
        
        self.conformancedate = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedate.append(val)
        
        self.conformancedatetype = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedatetype.append(val)
        
        self.conformancedegree = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:pass/gco:Boolean', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedegree.append(val)
        
        val = md.find(util.nspath_eval('gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString', namespaces))
        self.lineage = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
        self.specificationtitle = util.testXMLValue(val)

        self.specificationdate = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date', namespaces)):
            val = util.testXMLValue(i)
            if val is not None:
                self.specificationdate.append(val)

class SV_ServiceIdentification(object):
    """ process SV_ServiceIdentification """
    def __init__(self, md):
        val = md.find(util.nspath_eval('srv:serviceType/gco:LocalName', namespaces))
        self.type = util.testXMLValue(val)
      
        val = md.find(util.nspath_eval('srv:serviceTypeVersion/gco:CharacterString', namespaces))
        self.version = util.testXMLValue(val)

        val = md.find(util.nspath_eval('srv:accessProperties/gmd:MD_StandardOrderProcess/gmd:fees/gco:CharacterString', namespaces))
        self.fees = util.testXMLValue(val)

        val = md.find(util.nspath_eval('srv:extent/gmd:EX_Extent', namespaces))

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None

        self.couplingtype = _testCodeListValue(md.find(util.nspath_eval('gmd:couplingType/gmd:SV_CouplingType', namespaces)))

        self.operations = []

        for i in md.findall(util.nspath_eval('srv:containsOperations', namespaces)):
            tmp = {}
            val = i.find(util.nspath_eval('srv:SV_OperationMetadata/srv:operationName/gco:CharacterString', namespaces))
            tmp['name'] = util.testXMLValue(val)
            tmp['dcplist'] = []
            for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:DCP', namespaces)):
                tmp2 = _testCodeListValue(d.find(util.nspath_eval('srv:DCPList', namespaces)))
                tmp['dcplist'].append(tmp2)
         
            tmp['connectpoint'] = []
 
            for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:connectPoint', namespaces)):
                tmp3 = d.find(util.nspath_eval('gmd:CI_OnlineResource', namespaces))
                tmp['connectpoint'].append(CI_OnlineResource(tmp3))
            self.operations.append(tmp)

        self.operateson = []
         
        for i in md.findall(util.nspath_eval('srv:operatesOn', namespaces)):
            tmp = {}
            tmp['uuidref'] = i.attrib.get('uuidref')
            tmp['href'] = i.attrib.get(util.nspath_eval('xlink:href', namespaces))
            tmp['title'] = i.attrib.get(util.nspath_eval('xlink:title', namespaces))
            self.operateson.append(tmp)

class CI_OnlineResource(object):
    """ process CI_OnlineResource """
    def __init__(self,md):
        val = md.find(util.nspath_eval('gmd:linkage/gmd:URL', namespaces))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:protocol/gco:CharacterString', namespaces))
        self.protocol = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:name/gco:CharacterString', namespaces))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:description/gco:CharacterString', namespaces))
        self.description = util.testXMLValue(val)

        self.function = _testCodeListValue(md.find(util.nspath_eval('gmd:function/gmd:CI_OnLineFunctionCode', namespaces)))

class EX_Extent(object):
    """ process EX_Extent """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal', namespaces))
        self.minx = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal', namespaces))
        self.maxx = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal', namespaces))
        self.miny = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal', namespaces))
        self.maxy = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:EX_GeographicDescription/gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString', namespaces))
        self.description_code = util.testXMLValue(val)

class MD_ReferenceSystem(object):
    """ process MD_ReferenceSystem """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString', namespaces))
        self.code = util.testXMLValue(val)

def _testCodeListValue(elpath):
    if elpath is not None:
        return util.testXMLValue(elpath.attrib.get('codeListValue'), True)
    else:
        return None

class CodelistCatalogue(object):
    """ process CT_CodelistCatalogue """
    def __init__(self, ct):
        val = ct.find(util.nspath_eval('gmx:name/gco:CharacterString', namespaces))
        self.name = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:scope/gco:CharacterString', namespaces))
        self.scope = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:fieldOfApplication/gco:CharacterString', namespaces))
        self.fieldapp = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:versionNumber/gco:CharacterString', namespaces))
        self.version = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:versionDate/gco:Date', namespaces))
        self.date = util.testXMLValue(val)

        self.dictionaries = {}

        for i in ct.findall(util.nspath_eval('gmx:codelistItem/gmx:CodeListDictionary', namespaces)):
            id = i.attrib.get(util.nspath_eval('gml:id', namespaces))
            self.dictionaries[id] = {}
            val = i.find(util.nspath_eval('gml:description', namespaces))
            self.dictionaries[id]['description'] = util.testXMLValue(val)
            val = i.find(util.nspath_eval('gml:identifier', namespaces))
            self.dictionaries[id]['identifier'] = util.testXMLValue(val)
            self.dictionaries[id]['entries'] = {}

            for j in i.findall(util.nspath_eval('gmx:codeEntry', namespaces)):
                id2 = j.find(util.nspath_eval('gmx:CodeDefinition', namespaces)).attrib.get(util.nspath_eval('gml:id', namespaces))
                self.dictionaries[id]['entries'][id2] = {}
                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml:description', namespaces))
                self.dictionaries[id]['entries'][id2]['description'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml:identifier', namespaces))
                self.dictionaries[id]['entries'][id2]['identifier'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition', namespaces)).attrib.get('codeSpace')
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
