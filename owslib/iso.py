# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#           Angelos Tzotsos <tzotsos@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

""" ISO metadata parser """

import warnings

from owslib.etree import etree
from owslib import util
from owslib.namespaces import Namespaces


# default variables
def get_namespaces():
    n = Namespaces()
    ns = n.get_namespaces(["gco", "gfc", "gmd", "gmi", "gml", "gml32", "gmx", "gts", "srv", "xlink"])
    ns[None] = n.get_namespace("gmd")
    return ns


namespaces = get_namespaces()


class MD_Metadata(object):
    """ Process gmd:MD_Metadata """
    def __init__(self, md=None):

        if md is None:
            self.xml = None
            self.identifier = None
            self.parentidentifier = None
            self.language = None
            self.dataseturi = None
            self.languagecode = None
            self.datestamp = None
            self.charset = None
            self.hierarchy = None
            self.contact = []
            self.datetimestamp = None
            self.stdname = None
            self.stdver = None
            self.locales = []
            self.referencesystem = None
            self.identification = None
            self.contentinfo = None
            self.serviceidentification = None
            self.identificationinfo = []
            self.contentinfo = []
            self.distribution = None
            self.dataquality = None
            self.acquisition = None
        else:
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

            val = md.find(util.nspath_eval('gmd:dataSetURI/gco:CharacterString', namespaces))
            self.dataseturi = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces))
            self.languagecode = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(util.nspath_eval('gmd:dateStamp/gco:Date', namespaces))
            self.datestamp = util.testXMLValue(val)

            if not self.datestamp:
                val = md.find(util.nspath_eval('gmd:dateStamp/gco:DateTime', namespaces))
                self.datestamp = util.testXMLValue(val)

            self.charset = _testCodeListValue(md.find(
                util.nspath_eval('gmd:characterSet/gmd:MD_CharacterSetCode', namespaces)))

            self.hierarchy = _testCodeListValue(md.find(
                util.nspath_eval('gmd:hierarchyLevel/gmd:MD_ScopeCode', namespaces)))

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

            self.locales = []
            for i in md.findall(util.nspath_eval('gmd:locale/gmd:PT_Locale', namespaces)):
                self.locales.append(PT_Locale(i))

            val = md.find(util.nspath_eval('gmd:referenceSystemInfo/gmd:MD_ReferenceSystem', namespaces))
            if val is not None:
                self.referencesystem = MD_ReferenceSystem(val)
            else:
                self.referencesystem = None

            # TODO: merge .identificationinfo into .identification
            warnings.warn(
                'the .identification and .serviceidentification properties will merge into '
                '.identification being a list of properties.  This is currently implemented '
                'in .identificationinfo.  '
                'Please see https://github.com/geopython/OWSLib/issues/38 for more information',
                FutureWarning)

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

            self.identificationinfo = []
            for idinfo in md.findall(util.nspath_eval('gmd:identificationInfo', namespaces)):
                if len(idinfo) > 0:
                    val = list(idinfo)[0]
                    tagval = util.xmltag_split(val.tag)
                    if tagval == 'MD_DataIdentification':
                        self.identificationinfo.append(MD_DataIdentification(val, 'dataset'))
                    elif tagval == 'MD_ServiceIdentification':
                        self.identificationinfo.append(MD_DataIdentification(val, 'service'))
                    elif tagval == 'SV_ServiceIdentification':
                        self.identificationinfo.append(SV_ServiceIdentification(val))

            self.contentinfo = []
            for contentinfo in md.findall(
                    util.nspath_eval('gmd:contentInfo/gmd:MD_FeatureCatalogueDescription', namespaces)):
                self.contentinfo.append(MD_FeatureCatalogueDescription(contentinfo))
            for contentinfo in md.findall(
                    util.nspath_eval('gmd:contentInfo/gmd:MD_ImageDescription', namespaces)):
                self.contentinfo.append(MD_ImageDescription(contentinfo))

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

            val = md.find(util.nspath_eval('gmi:acquisitionInformation/gmi:MI_AcquisitionInformation', namespaces))
            if val is not None:
                self.acquisition = MI_AcquisitionInformation(val)

    def get_default_locale(self):
        """ get default gmd:PT_Locale based on gmd:language """

        for loc in self.locales:
            if loc.languagecode == self.language:
                return loc
        return None


class PT_Locale(object):
    """ process PT_Locale """

    def __init__(self, md=None):
        if md is None:
            self.id = None
            self.languagecode = None
            self.charset = None
        else:
            self.id = md.attrib.get('id')
            self.languagecode = md.find(
                util.nspath_eval('gmd:languageCode/gmd:LanguageCode', namespaces)).attrib.get('codeListValue')
            self.charset = md.find(
                util.nspath_eval('gmd:characterEncoding/gmd:MD_CharacterSetCode', namespaces)).attrib.get(
                    'codeListValue')


class CI_Date(object):
    """ process CI_Date """
    def __init__(self, md=None):
        if md is None:
            self.date = None
            self.type = None
        else:
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
            self.type = _testCodeListValue(val)


class CI_ResponsibleParty(object):
    """ process CI_ResponsibleParty """
    def __init__(self, md=None):

        if md is None:
            self.name = None
            self.organization = None
            self.position = None
            self.phone = None
            self.fax = None
            self.address = None
            self.city = None
            self.region = None
            self.postcode = None
            self.country = None
            self.email = None
            self.onlineresource = None
            self.role = None
        else:
            val = md.find(util.nspath_eval('gmd:individualName/gco:CharacterString', namespaces))
            self.name = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:organisationName/gco:CharacterString', namespaces))
            self.organization = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:positionName/gco:CharacterString', namespaces))
            self.position = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString', namespaces))

            self.phone = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString',
                namespaces))
            self.fax = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString',
                namespaces))
            self.address = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString', namespaces))
            self.city = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:administrativeArea/gco:CharacterString',
                namespaces))
            self.region = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString',
                namespaces))
            self.postcode = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:country/gco:CharacterString',
                namespaces))
            self.country = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',  # noqa
                namespaces))
            self.email = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource', namespaces))
            if val is not None:
                self.onlineresource = CI_OnlineResource(val)
            else:
                self.onlineresource = None

            self.role = _testCodeListValue(md.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode', namespaces)))


class MD_Keywords(object):
    """
    Class for the metadata MD_Keywords element
    """
    def __init__(self, md=None):
        if md is None:
            self.keywords = []
            self.type = None
            self.thesaurus = None
            self.kwdtype_codeList = 'http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/gmxCodelists.xml#MD_KeywordTypeCode'  # noqa
        else:
            self.keywords = []
            val = md.findall(util.nspath_eval('gmd:keyword/gco:CharacterString', namespaces))
            for word in val:
                self.keywords.append(util.testXMLValue(word))

            self.type = None
            val = md.find(util.nspath_eval('gmd:type/gmd:MD_KeywordTypeCode', namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            self.thesaurus = None
            val = md.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation', namespaces))
            if val is not None:
                self.thesaurus = {}

                thesaurus = val.find(util.nspath_eval('gmd:title/gco:CharacterString', namespaces))
                self.thesaurus['title'] = util.testXMLValue(thesaurus)

                thesaurus = val.find(util.nspath_eval('gmd:date/gmd:CI_Date/gmd:date/gco:Date', namespaces))
                self.thesaurus['date'] = util.testXMLValue(thesaurus)

                thesaurus = val.find(
                    util.nspath_eval('gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode', namespaces))
                self.thesaurus['datetype'] = util.testXMLAttribute(thesaurus, 'codeListValue')


class MD_DataIdentification(object):
    """ process MD_DataIdentification """
    def __init__(self, md=None, identtype=None):
        if md is None:
            self.identtype = None
            self.title = None
            self.alternatetitle = None
            self.aggregationinfo = None
            self.uricode = []
            self.uricodespace = []
            self.date = []
            self.datetype = []
            self.uselimitation = []
            self.uselimitation_url = []
            self.accessconstraints = []
            self.classification = []
            self.otherconstraints = []
            self.securityconstraints = []
            self.useconstraints = []
            self.denominators = []
            self.distance = []
            self.uom = []
            self.resourcelanguage = []
            self.resourcelanguagecode = []
            self.creator = []
            self.publisher = []
            self.contributor = []
            self.edition = None
            self.abstract = None
            self.abstract_url = None
            self.purpose = None
            self.status = None
            self.contact = []
            self.keywords = []
            self.keywords2 = []
            self.topiccategory = []
            self.supplementalinformation = None
            self.extent = None
            self.bbox = None
            self.temporalextent_start = None
            self.temporalextent_end = None
            self.spatialrepresentationtype = []
        else:
            self.identtype = identtype
            val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
            self.title = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString', namespaces))
            self.alternatetitle = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:aggregationInfo', namespaces))
            self.aggregationinfo = util.testXMLValue(val)

            self.uricode = []
            _values = md.findall(util.nspath_eval(
                'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:code/gco:CharacterString',
                namespaces))
            _values += md.findall(util.nspath_eval(
                'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString',
                namespaces))
            for i in _values:
                val = util.testXMLValue(i)
                if val is not None:
                    self.uricode.append(val)

            self.uricodespace = []
            for i in md.findall(util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.uricodespace.append(val)

            self.date = []
            self.datetype = []

            for i in md.findall(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date', namespaces)):
                self.date.append(CI_Date(i))

            self.uselimitation = []
            self.uselimitation_url = []
            _values = md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco:CharacterString', namespaces))
            _values += md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString', namespaces))
            for i in _values:
                val = util.testXMLValue(i)
                if val is not None:
                    self.uselimitation.append(val)

            _values = md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gmx:Anchor', namespaces))
            _values += md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gmx:Anchor', namespaces))
            for i in _values:
                val = util.testXMLValue(i)
                val1 = i.attrib.get(util.nspath_eval('xlink:href', namespaces))

                if val is not None:
                    self.uselimitation.append(val)
                    self.uselimitation_url.append(val1)

            self.accessconstraints = []
            for i in md.findall(util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.accessconstraints.append(val)

            self.classification = []
            for i in md.findall(util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_ClassificationCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.classification.append(val)

            self.otherconstraints = []
            for i in md.findall(util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.otherconstraints.append(val)

            self.securityconstraints = []
            for i in md.findall(util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification/gmd:MD_ClassificationCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.securityconstraints.append(val)

            self.useconstraints = []
            for i in md.findall(util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd:MD_RestrictionCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.useconstraints.append(val)

            self.denominators = []
            for i in md.findall(util.nspath_eval(
                    'gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer',  # noqa
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.denominators.append(val)

            self.distance = []
            self.uom = []
            for i in md.findall(util.nspath_eval(
                    'gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.distance.append(val)
                self.uom.append(i.get("uom"))

            self.resourcelanguagecode = []
            for i in md.findall(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.resourcelanguagecode.append(val)

            self.resourcelanguage = []
            for i in md.findall(util.nspath_eval('gmd:language/gco:CharacterString', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.resourcelanguage.append(val)

            self.creator = []
            self.publisher = []
            self.contributor = []
            for val in md.findall(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty', namespaces)):
                role = val.find(util.nspath_eval('gmd:role/gmd:CI_RoleCode', namespaces))
                if role is not None:
                    clv = _testCodeListValue(role)
                    rp = CI_ResponsibleParty(val)
                    if clv == 'originator':
                        self.creator.append(rp)
                    elif clv == 'publisher':
                        self.publisher.append(rp)
                    elif clv == 'author':
                        self.contributor.append(rp)

            val = md.find(util.nspath_eval('gmd:edition/gco:CharacterString', namespaces))
            self.edition = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:abstract/gco:CharacterString', namespaces))
            self.abstract = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:abstract/gmx:Anchor', namespaces))

            self.abstract_url = None
            if val is not None:
                self.abstract = util.testXMLValue(val)
                self.abstract_url = val.attrib.get(util.nspath_eval('xlink:href', namespaces))

            val = md.find(util.nspath_eval('gmd:purpose/gco:CharacterString', namespaces))
            self.purpose = util.testXMLValue(val)

            self.status = _testCodeListValue(md.find(util.nspath_eval('gmd:status/gmd:MD_ProgressCode', namespaces)))

            self.contact = []
            for i in md.findall(util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty', namespaces)):
                o = CI_ResponsibleParty(i)
                self.contact.append(o)

            self.spatialrepresentationtype = []
            for val in md.findall(util.nspath_eval(
                    'gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode', namespaces)):
                val = util.testXMLAttribute(val, 'codeListValue')
                if val:
                    self.spatialrepresentationtype.append(val)

            warnings.warn(
                'The .keywords and .keywords2 properties will merge into the '
                '.keywords property in the future, with .keywords becoming a list '
                'of MD_Keywords instances. This is currently implemented in .keywords2. '
                'Please see https://github.com/geopython/OWSLib/issues/301 for more information',
                FutureWarning)

            self.keywords = []

            for i in md.findall(util.nspath_eval('gmd:descriptiveKeywords', namespaces)):
                mdkw = {}
                mdkw['type'] = _testCodeListValue(i.find(util.nspath_eval(
                    'gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode', namespaces)))

                mdkw['thesaurus'] = {}

                val = i.find(util.nspath_eval(
                    'gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
                mdkw['thesaurus']['title'] = util.testXMLValue(val)

                val = i.find(util.nspath_eval(
                    'gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',
                    namespaces))
                mdkw['thesaurus']['date'] = util.testXMLValue(val)

                val = i.find(util.nspath_eval(
                    'gmd:MD_Keywords/gmd:thesaurusName/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode',  # noqa
                    namespaces))
                mdkw['thesaurus']['datetype'] = util.testXMLAttribute(val, 'codeListValue')

                mdkw['keywords'] = []

                for k in i.findall(util.nspath_eval('gmd:MD_Keywords/gmd:keyword', namespaces)):
                    val = k.find(util.nspath_eval('gco:CharacterString', namespaces))
                    if val is not None:
                        val2 = util.testXMLValue(val)
                        if val2 is not None:
                            mdkw['keywords'].append(val2)

                self.keywords.append(mdkw)

            self.keywords2 = []
            for mdkw in md.findall(util.nspath_eval('gmd:descriptiveKeywords/gmd:MD_Keywords', namespaces)):
                self.keywords2.append(MD_Keywords(mdkw))

            self.topiccategory = []
            for i in md.findall(util.nspath_eval('gmd:topicCategory/gmd:MD_TopicCategoryCode', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.topiccategory.append(val)

            val = md.find(util.nspath_eval('gmd:supplementalInformation/gco:CharacterString', namespaces))
            self.supplementalinformation = util.testXMLValue(val)

            # There may be multiple geographicElement, create an extent
            # from the one containing either an EX_GeographicBoundingBox or EX_BoundingPolygon.
            # The schema also specifies an EX_GeographicDescription. This is not implemented yet.
            val = None
            val2 = None
            val3 = None
            extents = md.findall(util.nspath_eval('gmd:extent', namespaces))
            extents.extend(md.findall(util.nspath_eval('srv:extent', namespaces)))
            for extent in extents:
                if val is None:
                    for e in extent.findall(util.nspath_eval('gmd:EX_Extent/gmd:geographicElement', namespaces)):
                        if e.find(util.nspath_eval('gmd:EX_GeographicBoundingBox', namespaces)) is not None or \
                                e.find(util.nspath_eval('gmd:EX_BoundingPolygon', namespaces)) is not None:
                            val = e
                            break
                    self.extent = EX_Extent(val)
                    self.bbox = self.extent.boundingBox  # for backwards compatibility

                if val2 is None:
                    val2 = extent.find(util.nspath_eval(
                        'gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition',  # noqa
                        namespaces))
                    if val2 is None:
                        val2 = extent.find(util.nspath_eval(
                            'gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:beginPosition',  # noqa
                            namespaces))
                    self.temporalextent_start = util.testXMLValue(val2)

                if val3 is None:
                    val3 = extent.find(util.nspath_eval(
                        'gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition',  # noqa
                        namespaces))
                    if val3 is None:
                        val3 = extent.find(util.nspath_eval(
                            'gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:endPosition',  # noqa
                            namespaces))
                    self.temporalextent_end = util.testXMLValue(val3)


class MD_Distributor(object):
    """ process MD_Distributor """
    def __init__(self, md=None):
        if md is None:
            self.contact = None
            self.online = []
        else:
            self.contact = None
            val = md.find(util.nspath_eval(
                'gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty', namespaces))
            if val is not None:
                self.contact = CI_ResponsibleParty(val)

            self.online = []

            for ol in md.findall(util.nspath_eval(
                'gmd:MD_Distributor/gmd:distributorTransferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource',  # noqa
                    namespaces)):
                self.online.append(CI_OnlineResource(ol))


class MD_Distribution(object):
    """ process MD_Distribution """
    def __init__(self, md=None):
        if md is None:
            self.format = None
            self.version = None
            self.distributor = []
            self.online = []
            pass
        else:
            val = md.find(util.nspath_eval(
                'gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString', namespaces))
            self.format = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString', namespaces))
            self.version = util.testXMLValue(val)

            self.distributor = []
            for dist in md.findall(util.nspath_eval('gmd:distributor', namespaces)):
                self.distributor.append(MD_Distributor(dist))

            self.online = []

            for ol in md.findall(util.nspath_eval(
                    'gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource',
                    namespaces)):
                self.online.append(CI_OnlineResource(ol))


class DQ_DataQuality(object):
    ''' process DQ_DataQuality'''
    def __init__(self, md=None):
        if md is None:
            self.conformancetitle = []
            self.conformancedate = []
            self.conformancedatetype = []
            self.conformancedegree = []
            self.lineage = None
            self.lineage_url = None
            self.specificationtitle = None
            self.specificationdate = []
        else:
            self.conformancetitle = []
            for i in md.findall(util.nspath_eval(
                    'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString',  # noqa
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.conformancetitle.append(val)

            self.conformancedate = []
            for i in md.findall(util.nspath_eval(
                    'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date',  # noqa
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.conformancedate.append(val)

            self.conformancedatetype = []
            for i in md.findall(util.nspath_eval(
                    'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode',  # noqa
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.conformancedatetype.append(val)

            self.conformancedegree = []
            for i in md.findall(util.nspath_eval(
                    'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:pass/gco:Boolean',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.conformancedegree.append(val)

            val = md.find(util.nspath_eval(
                'gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString', namespaces))
            self.lineage = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:lineage/gmd:LI_Lineage/gmd:statement/gmx:Anchor', namespaces))
            if val is not None:
                self.lineage = util.testXMLValue(val)
                self.lineage_url = val.attrib.get(util.nspath_eval('xlink:href', namespaces))

            val = md.find(util.nspath_eval(
                'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString',  # noqa
                namespaces))
            self.specificationtitle = util.testXMLValue(val)

            self.specificationdate = []
            for i in md.findall(util.nspath_eval(
                    'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date',  # noqa
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.specificationdate.append(val)


class SV_ServiceIdentification(object):
    """ process SV_ServiceIdentification """
    def __init__(self, md=None):
        if md is None:
            self.title = None
            self.abstract = None
            self.contact = None
            self.identtype = 'service'
            self.type = None
            self.version = None
            self.fees = None
            self.bbox = None
            self.couplingtype = None
            self.operations = []
            self.operateson = []
        else:
            val = md.find(util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString', namespaces))
            self.title = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:abstract/gco:CharacterString', namespaces))
            self.abstract = util.testXMLValue(val)

            self.contact = None
            val = md.find(util.nspath_eval(
                'gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty', namespaces))
            if val is not None:
                self.contact = CI_ResponsibleParty(val)

            self.identtype = 'service'
            val = md.find(util.nspath_eval('srv:serviceType/gco:LocalName', namespaces))
            self.type = util.testXMLValue(val)

            val = md.find(util.nspath_eval('srv:serviceTypeVersion/gco:CharacterString', namespaces))
            self.version = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'srv:accessProperties/gmd:MD_StandardOrderProcess/gmd:fees/gco:CharacterString', namespaces))
            self.fees = util.testXMLValue(val)

            val = md.find(util.nspath_eval('srv:extent/gmd:EX_Extent', namespaces))

            if val is not None:
                self.bbox = EX_Extent(val)
            else:
                self.bbox = None

            self.couplingtype = _testCodeListValue(md.find(util.nspath_eval(
                'gmd:couplingType/gmd:SV_CouplingType', namespaces)))

            self.operations = []

            for i in md.findall(util.nspath_eval('srv:containsOperations', namespaces)):
                tmp = {}
                val = i.find(util.nspath_eval(
                    'srv:SV_OperationMetadata/srv:operationName/gco:CharacterString', namespaces))
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
    def __init__(self, md=None):
        if md is None:
            self.url = None
            self.protocol = None
            self.name = None
            self.description = None
            self.function = None
        else:
            val = md.find(util.nspath_eval('gmd:linkage/gmd:URL', namespaces))
            self.url = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:protocol/gco:CharacterString', namespaces))
            self.protocol = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:name/gco:CharacterString', namespaces))
            self.name = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:description/gco:CharacterString', namespaces))
            self.description = util.testXMLValue(val)

            self.function = _testCodeListValue(md.find(util.nspath_eval(
                'gmd:function/gmd:CI_OnLineFunctionCode', namespaces)))


class EX_GeographicBoundingBox(object):
    def __init__(self, md=None):
        if md is None:
            self.minx = None
            self.maxx = None
            self.miny = None
            self.maxy = None
        else:
            val = md.find(util.nspath_eval('gmd:westBoundLongitude/gco:Decimal', namespaces))
            self.minx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gmd:eastBoundLongitude/gco:Decimal', namespaces))
            self.maxx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gmd:southBoundLatitude/gco:Decimal', namespaces))
            self.miny = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gmd:northBoundLatitude/gco:Decimal', namespaces))
            self.maxy = util.testXMLValue(val)


class EX_Polygon(object):
    def __init__(self, md=None):
        if md is None:
            self.exterior_ring = None
            self.interior_rings = []
        else:
            linear_ring = md.find(util.nspath_eval('gml32:Polygon/gml32:exterior/gml32:LinearRing', namespaces))
            if linear_ring is not None:
                self.exterior_ring = self._coordinates_for_ring(linear_ring)

            interior_ring_elements = md.findall(util.nspath_eval('gml32:Polygon/gml32:interior', namespaces))
            self.interior_rings = []
            for iring_element in interior_ring_elements:
                linear_ring = iring_element.find(util.nspath_eval('gml32:LinearRing', namespaces))
                self.interior_rings.append(self._coordinates_for_ring(linear_ring))

    def _coordinates_for_ring(self, linear_ring):
        coordinates = []
        positions = linear_ring.findall(util.nspath_eval('gml32:pos', namespaces))
        for pos in positions:
            tokens = pos.text.split()
            coords = tuple([float(t) for t in tokens])
            coordinates.append(coords)
        return coordinates


class EX_GeographicBoundingPolygon(object):
    def __init__(self, md=None):
        if md is None:
            self.is_extent = None
            self.polygons = []
        else:
            val = md.find(util.nspath_eval('gmd:extentTypeCode', namespaces))
            self.is_extent = util.testXMLValue(val)

            md_polygons = md.findall(util.nspath_eval('gmd:polygon', namespaces))

            self.polygons = []
            for val in md_polygons:
                self.polygons.append(EX_Polygon(val))


class EX_Extent(object):
    """ process EX_Extent """
    def __init__(self, md=None):
        if md is None:
            self.boundingBox = None
            self.boundingPolygon = None
            self.description_code = None
        else:
            self.boundingBox = None
            self.boundingPolygon = None

            if md is not None:
                bboxElement = md.find(util.nspath_eval('gmd:EX_GeographicBoundingBox', namespaces))
                if bboxElement is not None:
                    self.boundingBox = EX_GeographicBoundingBox(bboxElement)

                polygonElement = md.find(util.nspath_eval('gmd:EX_BoundingPolygon', namespaces))
                if polygonElement is not None:
                    self.boundingPolygon = EX_GeographicBoundingPolygon(polygonElement)

                val = md.find(util.nspath_eval(
                    'gmd:EX_GeographicDescription/gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString',  # noqa
                    namespaces))
                self.description_code = util.testXMLValue(val)


class MD_ReferenceSystem(object):
    """ process MD_ReferenceSystem """
    def __init__(self, md=None):
        if md is None:
            self.code = None
            self.codeSpace = None
            self.version = None
        else:
            val = md.find(util.nspath_eval(
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString', namespaces))
            if val is None:
                val = md.find(util.nspath_eval(
                    'gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gmx:Anchor', namespaces))
            if val is not None:
                self.code = util.testXMLValue(val)
            else:
                self.code = None

            val = md.find(util.nspath_eval(
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString', namespaces))
            if val is not None:
                self.codeSpace = util.testXMLValue(val)
            else:
                self.codeSpace = None

            val = md.find(util.nspath_eval(
                'gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:version/gco:CharacterString', namespaces))
            if val is not None:
                self.version = util.testXMLValue(val)
            else:
                self.version = None


def _testCodeListValue(elpath):
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
            id = i.attrib.get(util.nspath_eval('gml32:id', namespaces))
            self.dictionaries[id] = {}
            val = i.find(util.nspath_eval('gml32:description', namespaces))
            self.dictionaries[id]['description'] = util.testXMLValue(val)
            val = i.find(util.nspath_eval('gml32:identifier', namespaces))
            self.dictionaries[id]['identifier'] = util.testXMLValue(val)
            self.dictionaries[id]['entries'] = {}

            for j in i.findall(util.nspath_eval('gmx:codeEntry', namespaces)):
                id2 = j.find(util.nspath_eval('gmx:CodeDefinition', namespaces)).attrib.get(
                    util.nspath_eval('gml32:id', namespaces))
                self.dictionaries[id]['entries'][id2] = {}
                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml32:description', namespaces))
                self.dictionaries[id]['entries'][id2]['description'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition/gml32:identifier', namespaces))
                self.dictionaries[id]['entries'][id2]['identifier'] = util.testXMLValue(val)

                val = j.find(util.nspath_eval('gmx:CodeDefinition', namespaces)).attrib.get('codeSpace')
                self.dictionaries[id]['entries'][id2]['codespace'] = util.testXMLValue(val, True)

    def getcodelistdictionaries(self):
        return list(self.dictionaries.keys())

    def getcodedefinitionidentifiers(self, cdl):
        if cdl in self.dictionaries:
            ids = []
            for i in self.dictionaries[cdl]['entries']:
                ids.append(self.dictionaries[cdl]['entries'][i]['identifier'])
            return ids
        else:
            return None


class MD_FeatureCatalogueDescription(object):
    """Process gmd:MD_FeatureCatalogueDescription"""
    def __init__(self, fcd=None):
        if fcd is None:
            self.xml = None
            self.compliancecode = None
            self.language = []
            self.includedwithdataset = None
            self.featuretypenames = []
            self.featurecatalogues = []
        else:
            if hasattr(fcd, 'getroot'):  # standalone document
                self.xml = etree.tostring(fcd.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(fcd)

            self.compliancecode = None
            val = fcd.find(util.nspath_eval('gmd:complianceCode/gco:Boolean', namespaces))
            val = util.testXMLValue(val)
            if val is not None:
                self.compliancecode = util.getTypedValue('boolean', val)

            self.language = []
            for i in fcd.findall(util.nspath_eval('gmd:language/gco:CharacterString', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.language.append(val)

            self.includedwithdataset = None
            val = fcd.find(util.nspath_eval('gmd:includedWithDataset/gco:Boolean', namespaces))
            val = util.testXMLValue(val)
            if val is not None:
                self.includedwithdataset = util.getTypedValue('boolean', val)

            self.featuretypenames = []
            for i in fcd.findall(util.nspath_eval('gmd:featureTypes/gco:LocalName', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.featuretypenames.append(val)
            for i in fcd.findall(util.nspath_eval('gmd:featureTypes/gco:ScopedName', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.featuretypenames.append(val)

            self.featurecatalogues = []
            for i in fcd.findall(util.nspath_eval('gmd:featureCatalogueCitation', namespaces)):
                val = i.attrib.get('uuidref')
                val = util.testXMLValue(val, attrib=True)
                if val is not None:
                    self.featurecatalogues.append(val)


class FC_FeatureCatalogue(object):
    """Process gfc:FC_FeatureCatalogue"""
    def __init__(self, fc=None):
        if fc is None:
            self.xml = None
            self.identifier = None
            self.name = None
            self.versiondate = None
            self.producer = None
            self.featuretypes = []
        else:
            if hasattr(fc, 'getroot'):  # standalone document
                self.xml = etree.tostring(fc.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(fc)

            val = fc.attrib['uuid']
            self.identifier = util.testXMLValue(val, attrib=True)

            val = fc.find(util.nspath_eval('gmx:name/gco:CharacterString', namespaces))
            self.name = util.testXMLValue(val)

            val = fc.find(util.nspath_eval('gmx:versionDate/gco:Date', namespaces))
            self.versiondate = util.testXMLValue(val)

            if not self.versiondate:
                val = fc.find(util.nspath_eval('gmx:versionDate/gco:DateTime', namespaces))
                self.versiondate = util.testXMLValue(val)

            self.producer = None
            prod = fc.find(util.nspath_eval('gfc:producer/gmd:CI_ResponsibleParty', namespaces))
            if prod is not None:
                self.producer = CI_ResponsibleParty(prod)

            self.featuretypes = []
            for i in fc.findall(util.nspath_eval('gfc:featureType/gfc:FC_FeatureType', namespaces)):
                self.featuretypes.append(FC_FeatureType(i))


class FC_FeatureType(object):
    """Process gfc:FC_FeatureType"""
    def __init__(self, ft=None):
        if ft is None:
            self.xml = None
            self.identifier = None
            self.typename = None
            self.definition = None
            self.isabstract = None
            self.aliases = []
            self.attributes = []
        else:
            if hasattr(ft, 'getroot'):  # standalone document
                self.xml = etree.tostring(ft.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(ft)

            val = ft.attrib['uuid']
            self.identifier = util.testXMLValue(val, attrib=True)

            val = ft.find(util.nspath_eval('gfc:typeName/gco:LocalName', namespaces))
            self.typename = util.testXMLValue(val)

            val = ft.find(util.nspath_eval('gfc:definition/gco:CharacterString', namespaces))
            self.definition = util.testXMLValue(val)

            self.isabstract = None
            val = ft.find(util.nspath_eval('gfc:isAbstract/gco:Boolean', namespaces))
            val = util.testXMLValue(val)
            if val is not None:
                self.isabstract = util.getTypedValue('boolean', val)

            self.aliases = []
            for i in ft.findall(util.nspath_eval('gfc:aliases/gco:LocalName', namespaces)):
                self.aliases.append(util.testXMLValue(i))

            self.attributes = []
            for i in ft.findall(util.nspath_eval('gfc:carrierOfCharacteristics/gfc:FC_FeatureAttribute', namespaces)):
                self.attributes.append(FC_FeatureAttribute(i))


class FC_FeatureAttribute(object):
    """Process gfc:FC_FeatureAttribute"""
    def __init__(self, fa=None):
        if fa is None:
            self.xml = None
            self.membername = None
            self.definition = None
            self.code = None
            self.valuetype = None
            self.listedvalues = []
        else:
            if hasattr(fa, 'getroot'):  # standalone document
                self.xml = etree.tostring(fa.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(fa)

            val = fa.find(util.nspath_eval('gfc:memberName/gco:LocalName', namespaces))
            self.membername = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:definition/gco:CharacterString', namespaces))
            self.definition = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:code/gco:CharacterString', namespaces))
            self.code = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:valueType/gco:TypeName/gco:aName/gco:CharacterString', namespaces))
            self.valuetype = util.testXMLValue(val)

            self.listedvalues = []
            for i in fa.findall(util.nspath_eval('gfc:listedValue/gfc:FC_ListedValue', namespaces)):
                self.listedvalues.append(FC_ListedValue(i))


class FC_ListedValue(object):
    """Process gfc:FC_ListedValue"""
    def __init__(self, lv=None):
        if lv is None:
            self.xml = None
            self.label = None
            self.code = None
            self.definition = None
        else:
            if hasattr(lv, 'getroot'):  # standalone document
                self.xml = etree.tostring(lv.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(lv)

            val = lv.find(util.nspath_eval('gfc:label/gco:CharacterString', namespaces))
            self.label = util.testXMLValue(val)

            val = lv.find(util.nspath_eval('gfc:code/gco:CharacterString', namespaces))
            self.code = util.testXMLValue(val)

            val = lv.find(util.nspath_eval('gfc:definition/gco:CharacterString', namespaces))
            self.definition = util.testXMLValue(val)


class MD_ImageDescription(object):
    """Process gmd:MD_ImageDescription"""
    def __init__(self, img_desc=None):
        self.type = 'image'
        self.bands = []

        if img_desc is None:
            self.attribute_description = None
            self.cloud_cover = None
            self.processing_level = None
        else:
            val = img_desc.find(util.nspath_eval('gmd:attributeDescription/gco:RecordType', namespaces))
            self.attribute_description = util.testXMLValue(val)

            val = img_desc.find(util.nspath_eval('gmd:contentType/gmd:MD_CoverageContentTypeCode', namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            val = img_desc.find(util.nspath_eval('gmd:cloudCoverPercentage/gco:Real', namespaces))
            self.cloud_cover = util.testXMLValue(val)

            val = img_desc.find(util.nspath_eval(
                'gmd:processingLevelCode/gmd:RS_Identifier/gmd:code/gco:CharacterString', namespaces))
            self.processing_level = util.testXMLValue(val)

            for i in img_desc.findall(util.nspath_eval('gmd:dimension/gmd:MD_Band', namespaces)):
                bid = util.testXMLAttribute(i, 'id')
                self.bands.append(MD_Band(i, bid))


class MD_Band(object):
    """Process gmd:MD_Band"""
    def __init__(self, band, band_id=None):
        if band is None:
            self.id = None
            self.units = None
            self.min = None
            self.max = None
        else:
            self.id = band_id

            val = band.find(util.nspath_eval('gmd:units/gml:UnitDefinition/gml:identifier', namespaces))
            self.units = util.testXMLValue(val)

            val = band.find(util.nspath_eval('gmd:minValue/gco:Real', namespaces))
            self.min = util.testXMLValue(val)

            val = band.find(util.nspath_eval('gmd:maxValue/gco:Real', namespaces))
            self.max = util.testXMLValue(val)


class MI_AcquisitionInformation(object):
    """Process gmi:MI_AcquisitionInformation"""

    def __init__(self, acq=None):
        self.platforms = []

        for i in acq.findall(util.nspath_eval('gmi:platform/gmi:MI_Platform', namespaces)):
            self.platforms.append(MI_Platform(i))


class MI_Platform(object):
    """Process gmi:MI_Platform"""

    def __init__(self, plt=None):
        self.instruments = []

        if plt is None:
            self.identifier = None
            self.description = None
        else:
            val = plt.find(util.nspath_eval('gmi:identifier', namespaces))
            self.identifier = util.testXMLValue(val)

            val = plt.find(util.nspath_eval('gmi:description', namespaces))
            self.description = util.testXMLValue(val)

            for i in plt.findall(util.nspath_eval('gmi:instrument/gmi:MI_Instrument', namespaces)):
                self.instruments.append(MI_Instrument(i))


class MI_Instrument(object):
    """Process gmi:MI_Instrument"""

    def __init__(self, inst=None):
        if inst is None:
            self.identifier = None
            self.type = None
        else:
            val = inst.find(util.nspath_eval('gmi:identifier', namespaces))
            self.identifier = util.testXMLValue(val)

            val = inst.find(util.nspath_eval('gmi:type', namespaces))
            self.type = util.testXMLValue(val)
