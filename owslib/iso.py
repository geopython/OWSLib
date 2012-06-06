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

class MD_Metadata(object):
    """ Process gmd:MD_Metadata """
    def __init__(self, md):

        if hasattr(md, 'getroot'):  # standalone document
            self.xml = etree.tostring(md.getroot())
        else:  # part of a larger document
            self.xml = etree.tostring(md)

        val = md.find(util.nspath_eval('gmd:fileIdentifier/gco:CharacterString'))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:parentIdentifier/gco:CharacterString'))
        self.parentidentifier = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:language/gco:CharacterString'))
        self.language = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:datasetURI/gco:CharacterString'))
        self.dataseturi = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:language/gmd:LanguageCode'))
        self.languagecode = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:dateStamp/gco:Date'))
        self.datestamp = util.testXMLValue(val)

        if not self.datestamp:
            val = md.find(util.nspath_eval('gmd:dateStamp/gco:DateTime'))
            self.datestamp = util.testXMLValue(val)

        self.charset = _test_code_list_value(md.find(util.nspath_eval('gmd:characterSet/gmd:MD_CharacterSetCode')))
  
        self.hierarchy = _test_code_list_value(md.find(util.nspath_eval('gmd:hierarchyLevel/gmd:MD_ScopeCode')))

        self.contact = []
        for i in md.findall(util.nspath_eval('gmd:contact/gmd:CI_ResponsibleParty')):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        val = md.find(util.nspath_eval('gmd:dateStamp/gco:DateTime'))
        self.datetimestamp = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:metadataStandardName/gco:CharacterString'))
        self.stdname = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:metadataStandardVersion/gco:CharacterString'))
        self.stdver = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:referenceSystemInfo/gmd:MD_ReferenceSystem'))
        if val is not None:
            self.referencesystem = MD_ReferenceSystem(val)
        else:
            self.referencesystem = None

        val = md.find(util.nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification'))
        val2 = md.find(util.nspath_eval('gmd:identificationInfo/srv:SV_ServiceIdentification'))

        if val is not None:
            self.identification = MD_DataIdentification(val, 'dataset')
            self.serviceidentification = None
        elif val2 is not None:
            self.identification = MD_DataIdentification(val2, 'service')
            self.serviceidentification = SV_ServiceIdentification(val2)
        else:
            self.identification = None
            self.serviceidentification = None

        val = md.find(util.nspath_eval('gmd:distributionInfo/gmd:MD_Distribution'))
        if val is not None:
            self.distribution = MD_Distribution(val)
        else:
            self.distribution = None
        
        val = md.find(util.nspath_eval('gmd:dataQualityInfo/gmd:DQ_DataQuality'))
        if val is not None:
            self.dataquality = DQ_DataQuality(val)
        else:
            self.dataquality = None

class CI_Date(object):
    """ process CI_Date """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:date/gco:Date'))
        if val is not None:
            self.date = util.testXMLValue(val)
        else:
            val = md.find(util.nspath_eval('gmd:date/gco:DateTime'))
            if val is not None:
                self.date = util.testXMLValue(val)
            else:
                self.date = None

        val = md.find(util.nspath_eval('gmd:dateType/gmd:CI_DateTypeCode'))
        self.type = _test_code_list_value(val)

class CI_ResponsibleParty(object):
    """ process CI_ResponsibleParty """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:individualName/gco:CharacterString'))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:organisationName/gco:CharacterString'))
        self.organization = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:positionName/gco:CharacterString'))
        self.position = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString'))

        self.phone = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString'))
        self.fax = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString'))
        self.address = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString'))
        self.city = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString'))
        self.region = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString'))
        self.postcode = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString'))
        self.country = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'))
        self.email = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource'))
        if val is not None:
          self.onlineresource = CI_OnlineResource(val)
        else:
          self.onlineresource = None
      
        self.role = _test_code_list_value(md.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode')))

class MD_DataIdentification(object):
    """ process MD_DataIdentification """
    def __init__(self, md, identtype):
        self.identtype = identtype
        val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString'))
        self.title = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString'))
        self.alternatetitle = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:aggregationInfo'))
        self.aggregationinfo = util.testXMLValue(val)

        self.date = []
        self.datetype = []
        
        for i in md.findall(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date')):
            self.date.append(CI_Date(i))
        
        self.uselimitation = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString')):
            val = util.testXMLValue(i)
            if val is not None:
                self.uselimitation.append(val)
        
        self.accessconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode')):
            val = _test_code_list_value(i)
            if val is not None:
                self.accessconstraints.append(val)
        
        self.classification = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_ClassificationCode')):
            val = _test_code_list_value(i)
            if val is not None:
                self.classification.append(val)
        
        self.otherconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString')):
            val = util.testXMLValue(i)
            if val is not None:
                self.otherconstraints.append(val)

        self.securityconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:useLimitation')):
            val = util.testXMLValue(i)
            if val is not None:
                self.securityconstraints.append(val)

        self.useconstraints = []
        for i in md.findall(util.nspath_eval('gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd:MD_RestrictionCode')):
            val = _test_code_list_value(i)
            if val is not None:
                self.useconstraints.append(val)
        
        self.denominators = []
        for i in md.findall(util.nspath_eval('gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer')):
            val = util.testXMLValue(i)
            if val is not None:
                self.denominators.append(val)
        
        self.distance = []
        self.uom = []
        for i in md.findall(util.nspath_eval('gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance')):
            val = util.testXMLValue(i)
            if val is not None:
                self.distance.append(val)
            self.uom.append(i.get("uom"))
        
        self.resourcelanguage = []
        for i in md.findall(util.nspath_eval('gmd:language/gmd:LanguageCode')):
            val = _test_code_list_value(i)
            if val is not None:
                self.resourcelanguage.append(val)

        val = md.find(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty/gmd:organisationName'))
        if val is not None:
            val2 = val.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode')) 
            if val2 is not None:
                clv = _test_code_list_value(val)
                if clv == 'originator':
                    self.creator = util.testXMLValue(val)
                elif clv == 'publisher':
                    self.publisher = util.testXMLValue(val)
                elif clv == 'contributor':
                    self.originator = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:edition/gco:CharacterString'))
        self.edition = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:abstract/gco:CharacterString'))
        self.abstract = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:purpose/gco:CharacterString'))
        self.purpose = util.testXMLValue(val, True)

        self.status = _test_code_list_value(md.find(util.nspath_eval('gmd:status/gmd:MD_ProgressCode')))

        self.contact = []
        for i in md.findall(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty')):
            o = CI_ResponsibleParty(i)
            self.contact.append(o)
        
        self.keywords = []

        for i in md.findall(util.nspath_eval('gmd:descriptiveKeywords')):
            mdkw = {}
            mdkw['type'] = _test_code_list_value(i.find(util.nspath_eval('gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode')))

            mdkw['thesaurus'] = {}

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString'))
            mdkw['thesaurus']['title'] = util.testXMLValue(val)

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date'))
            mdkw['thesaurus']['date'] = util.testXMLValue(val)

            val = i.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode'))
            mdkw['thesaurus']['datetype'] = util.testXMLValue(val)

            mdkw['keywords'] = []

            for k in i.findall(util.nspath_eval('gmd:MD_Keywords/gmd:keyword')):
                val = k.find(util.nspath_eval('gco:CharacterString'))
                if val is not None:
                    val2 = util.testXMLValue(val) 
                    if val2 is not None:
                        mdkw['keywords'].append(val2)

            self.keywords.append(mdkw)

        self.topiccategory = []
        for i in md.findall(util.nspath_eval('gmd:topicCategory/gmd:MD_TopicCategoryCode')):
            val = util.testXMLValue(i)
            if val is not None:
                self.topiccategory.append(val)
        
        val = md.find(util.nspath_eval('gmd:supplementalInformation/gco:CharacterString'))
        self.supplementalinformation = util.testXMLValue(val)
        
        # there may be multiple geographicElement, create an extent
        # from the one containing an EX_GeographicBoundingBox
        val = None
        for e in md.findall(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:geographicElement')):
            if e.find(util.nspath_eval('gmd:EX_GeographicBoundingBox')) is not None:
                val = e
                break

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None
        
        val = md.find(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition'))
        self.temporalextent_start = util.testXMLValue(val)
        
        self.temporalextent_end = []
        val = md.find(util.nspath_eval('gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition'))
        self.temporalextent_end = util.testXMLValue(val)
        
class MD_Distribution(object):
    """ process MD_Distribution """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString'))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString'))
        self.version = util.testXMLValue(val)

        self.online = []

        for ol in md.findall(util.nspath_eval('gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource')):
            self.online.append(CI_OnlineResource(ol))
        
class DQ_DataQuality(object):
    ''' process DQ_DataQuality'''
    def __init__(self, md):
        
        self.conformancetitle = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString')):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancetitle.append(val)
        
        self.conformancedate = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date')):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedate.append(val)
        
        self.conformancedatetype = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode')):
            val = _test_code_list_value(i)
            if val is not None:
                self.conformancedatetype.append(val)
        
        self.conformancedegree = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:pass/gco:Boolean')):
            val = util.testXMLValue(i)
            if val is not None:
                self.conformancedegree.append(val)
        
        val = md.find(util.nspath_eval('gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString'))
        self.lineage = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString'))
        self.specificationtitle = util.testXMLValue(val)

        self.specificationdate = []
        for i in md.findall(util.nspath_eval('gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date')):
            val = util.testXMLValue(i)
            if val is not None:
                self.specificationdate.append(val)

class SV_ServiceIdentification(object):
    """ process SV_ServiceIdentification """
    def __init__(self, md):
        val = md.find(util.nspath_eval('srv:serviceType/gco:LocalName'))
        self.type = util.testXMLValue(val)
      
        val = md.find(util.nspath_eval('srv:serviceTypeVersion/gco:CharacterString'))
        self.version = util.testXMLValue(val)

        val = md.find(util.nspath_eval('srv:accessProperties/gmd:MD_StandardOrderProcess/gmd:fees/gco:CharacterString'))
        self.fees = util.testXMLValue(val)

        val = md.find(util.nspath_eval('srv:extent/gmd:EX_Extent'))

        if val is not None:
            self.bbox = EX_Extent(val)
        else:
            self.bbox = None

        self.couplingtype = _test_code_list_value(md.find(util.nspath_eval('gmd:couplingType/gmd:SV_CouplingType')))

        self.operations = []

        for i in md.findall(util.nspath_eval('srv:containsOperations')):
            tmp = {}
            val = i.find(util.nspath_eval('srv:SV_OperationMetadata/srv:operationName/gco:CharacterString'))
            tmp['name'] = util.testXMLValue(val)
            tmp['dcplist'] = []
            for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:DCP')):
                tmp2 = _test_code_list_value(d.find(util.nspath_eval('srv:DCPList')))
                tmp['dcplist'].append(tmp2)
         
            tmp['connectpoint'] = []
 
            for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:connectPoint')):
                tmp3 = d.find(util.nspath_eval('gmd:CI_OnlineResource'))
                tmp['connectpoint'].append(CI_OnlineResource(tmp3))
            self.operations.append(tmp)

        self.operateson = []
         
        for i in md.findall(util.nspath_eval('srv:operatesOn')):
            tmp = {}
            tmp['uuidref'] = i.attrib.get('uuidref')
            tmp['href'] = i.attrib.get(util.nspath_eval('xlink:href'))
            tmp['title'] = i.attrib.get(util.nspath_eval('xlink:title'))
            self.operateson.append(tmp)

class CI_OnlineResource(object):
    """ process CI_OnlineResource """
    def __init__(self,md):
        val = md.find(util.nspath_eval('gmd:linkage/gmd:URL'))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:protocol/gco:CharacterString'))
        self.protocol = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:name/gco:CharacterString'))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:description/gco:CharacterString'))
        self.description = util.testXMLValue(val)

        self.function = _test_code_list_value(md.find(util.nspath_eval('gmd:function/gmd:CI_OnLineFunctionCode')))

class EX_Extent(object):
    """ process EX_Extent """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:westBoundLongitude/gco:Decimal'))
        self.minx = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:eastBoundLongitude/gco:Decimal'))
        self.maxx = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:southBoundLatitude/gco:Decimal'))
        self.miny = util.testXMLValue(val)
        val = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:northBoundLatitude/gco:Decimal'))
        self.maxy = util.testXMLValue(val)

        val = md.find(util.nspath_eval('gmd:EX_GeographicDescription/gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString'))
        self.description_code = util.testXMLValue(val)

class MD_ReferenceSystem(object):
    """ process MD_ReferenceSystem """
    def __init__(self, md):
        val = md.find(util.nspath_eval('gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString'))
        self.code = util.testXMLValue(val)

def _test_code_list_value(elpath):
    """ get gco:CodeListValue_Type attribute, else get text content """
    if elpath is not None:  # try to get @codeListValue
        val = util.testXMLValue(elpath.attrib.get('codeListValue'), True)
        if val is not None:
            return val
        else:  # see if there is element text
            return util.testXMLValue(elpath)
    else:
        return None

class CodelistCatalogue(object):
    """ process CT_CodelistCatalogue """
    def __init__(self, ct):
        val = ct.find(util.nspath_eval('gmx:name/gco:CharacterString'))
        self.name = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:scope/gco:CharacterString'))
        self.scope = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:fieldOfApplication/gco:CharacterString'))
        self.fieldapp = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:versionNumber/gco:CharacterString'))
        self.version = util.testXMLValue(val)
        val = ct.find(util.nspath_eval('gmx:versionDate/gco:Date'))
        self.date = util.testXMLValue(val)

        self.dictionaries = {}

        for i in ct.findall(util.nspath_eval('gmx:codelistItem/gmx:CodeListDictionary')):
            id = i.attrib.get(util.nspath_eval('gml32:id'))
            self.dictionaries[id] = {}
            val = i.find(util.nspath_eval('gml32:description'))
            self.dictionaries[id]['description'] = util.testXMLValue(val)
            val = i.find(util.nspath_eval('gml32:identifier'))
            self.dictionaries[id]['identifier'] = util.testXMLValue(val)
            self.dictionaries[id]['entries'] = {}

            for j in i.findall(util.nspath_eval('gmx:codeEntry')):
                id2 = j.find(util.nspath_eval('gmx:CodeDefinition')).attrib.get(util.nspath_eval('gml32:id'))
                self.dictionaries[id]['entries'][id2] = {}
                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml32:description'))
                self.dictionaries[id]['entries'][id2]['description'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml32:identifier'))
                self.dictionaries[id]['entries'][id2]['identifier'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition')).attrib.get('codeSpace')
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
