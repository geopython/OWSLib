# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2023 CSIRO Australia
#
# Author : Vincent Fazio
#
# Contact email: vincent.fazio@csiro.au
# =============================================================================

# flake8: noqa: E501

""" ISO 19115 Part 3 XML metadata parser

    Parsing is initiated by passing in etree root Element to the 'MD_Metadata' constructor:

    from owslib.etree import etree
    from owslib.iso_3 import MD_Metadata

    exml = etree.fromstring(xml_bytes)
    mdb = MD_Metadata(exml)
"""

from owslib.etree import etree
from owslib import util


# ISO 19115 Part 3 XML namespaces
namespaces = {
        "mdb":"http://standards.iso.org/iso/19115/-3/mdb/2.0",
        "cat":"http://standards.iso.org/iso/19115/-3/cat/1.0",
        "gfc":"http://standards.iso.org/iso/19110/gfc/1.1",
        "cit":"http://standards.iso.org/iso/19115/-3/cit/2.0",
        "gcx":"http://standards.iso.org/iso/19115/-3/gcx/1.0",
        "gex":"http://standards.iso.org/iso/19115/-3/gex/1.0",
        "lan":"http://standards.iso.org/iso/19115/-3/lan/1.0",
        "srv":"http://standards.iso.org/iso/19115/-3/srv/2.1",
        "mas":"http://standards.iso.org/iso/19115/-3/mas/1.0",
        "mcc":"http://standards.iso.org/iso/19115/-3/mcc/1.0",
        "mco":"http://standards.iso.org/iso/19115/-3/mco/1.0",
        "mda":"http://standards.iso.org/iso/19115/-3/mda/1.0",
        "mds":"http://standards.iso.org/iso/19115/-3/mds/2.0",
        "mdt":"http://standards.iso.org/iso/19115/-3/mdt/2.0",
        "mex":"http://standards.iso.org/iso/19115/-3/mex/1.0",
        "mmi":"http://standards.iso.org/iso/19115/-3/mmi/1.0",
        "mpc":"http://standards.iso.org/iso/19115/-3/mpc/1.0",
        "mrc":"http://standards.iso.org/iso/19115/-3/mrc/2.0",
        "mrd":"http://standards.iso.org/iso/19115/-3/mrd/1.0",
        "mri":"http://standards.iso.org/iso/19115/-3/mri/1.0",
        "mrl":"http://standards.iso.org/iso/19115/-3/mrl/2.0",
        "mrs":"http://standards.iso.org/iso/19115/-3/mrs/1.0",
        "msr":"http://standards.iso.org/iso/19115/-3/msr/2.0",
        "mdq":"http://standards.iso.org/iso/19157/-2/mdq/1.0",
        "mac":"http://standards.iso.org/iso/19115/-3/mac/2.0",
        "gco":"http://standards.iso.org/iso/19115/-3/gco/1.0",
        "gml":"http://www.opengis.net/gml",
        "xlink":"http://www.w3.org/1999/xlink",
        "xsi":"http://www.w3.org/2001/XMLSchema-instance"
}

class printable():
    """ A super class used to roughly pretty print class members

        Usage:

        mdb = MD_Metadata(exml)
        print(mdb.format_me())

    """

    def format_me(self, idx=0):
        """ Returns a formatted string version of class

        :param idx: optional indentation index, internal use only, used for 'printable' member classes
        :returns: string version of class and members
        """
        repr_str = "\n"
        for d in dir(self):
            if not d.startswith("__") and not callable(getattr(self,d)):
                if isinstance(getattr(self,d), (str, bytes)):
                    repr_str += "  " * idx + f"{self.__class__.__name__}:{d}='{getattr(self,d)[:100]}'\n"
                elif isinstance(getattr(self,d), list):
                    repr_str += "  " * idx + f"{self.__class__.__name__}:{d}=[\n"
                    for item in getattr(self,d):
                        if isinstance(item, printable):
                            repr_str += "  " * idx + f"  {item.format_me(idx+1)}"
                        elif item is not None:
                            repr_str += "  " * idx + f"  {item}\n"
                    repr_str += "  " * idx + "]\n"
                elif isinstance(getattr(self,d), printable):
                    repr_str += "  " * idx + f"{self.__class__.__name__}:{d}={getattr(self,d).format_me(idx+1)}"
        return repr_str


class MD_Metadata(printable):
    """ Process mdb:MD_Metadata
    """
    def __init__(self, md=None):
        """
        Parses XML root tree

        :param md: etree.Element root
        """
        if md is None:
            self.md = None
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
            self.identification = []
            self.contentinfo = []
            self.distribution = None
            self.dataquality = None
            self.acquisition = None
        else:
            self.md = md
            if hasattr(md, 'getroot'):  # standalone document
                self.xml = etree.tostring(md.getroot())
            else:  # part of a larger document
                self.xml = etree.tostring(md)

            val = md.find(util.nspath_eval('mdb:metadataIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', namespaces))
            self.identifier = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:parentMetadata/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', namespaces))
            self.parentidentifier = util.testXMLValue(val)

            val = md.find(util.nspath_eval('lan:language/gco:CharacterString', namespaces))
            self.language = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', namespaces))
            self.dataseturi = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:defaultLocale/lan:PT_Locale/lan:language/lan:LanguageCode', namespaces))
            self.languagecode = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(util.nspath_eval('mdb:dateInfo/cit:CI_Date/cit:date/gco:DateTime', namespaces))
            self.datestamp = util.testXMLValue(val)

            val = md.find(
                util.nspath_eval('mdb:defaultLocale/lan:PT_Locale/lan:characterEncoding/lan:MD_CharacterSetCode', namespaces))
            self.charset = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(
                util.nspath_eval('mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode', namespaces))
            self.hierarchy = util.testXMLAttribute(val, 'codeListValue')

            self.contact = []
            for i in md.findall(util.nspath_eval('mdb:contact/cit:CI_Responsibility', namespaces)):
                o = CI_Responsibility(i)
                self.contact.append(o)

            self.datetimestamp = self.datestamp

            val = md.find(util.nspath_eval('mdb:metadataStandard/cit:CI_Citation/cit:title/gco:CharacterString', namespaces))
            self.stdname = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:metadataStandard/cit:CI_Citation/cit:edition/gco:CharacterString', namespaces))
            self.stdver = util.testXMLValue(val)

            self.locales = []
            for i in md.findall(util.nspath_eval('mdb:defaultLocale/lan:PT_Locale', namespaces)):
                self.locales.append(PT_Locale(i))

            val = md.find(util.nspath_eval('mdb:referenceSystemInfo/mrs:MD_ReferenceSystem', namespaces))
            if val is not None:
                self.referencesystem = MD_ReferenceSystem(val)
            else:
                self.referencesystem = None

            self.identification = []

            for idinfo in md.findall(util.nspath_eval('mdb:identificationInfo', namespaces)):
                if len(idinfo) > 0:
                    val = list(idinfo)[0]
                    tagval = util.xmltag_split(val.tag)
                    if tagval == 'MD_DataIdentification':
                        self.identification.append(MD_DataIdentification(val, 'dataset'))
                    elif tagval == 'MD_ServiceIdentification':
                        self.identification.append(MD_DataIdentification(val, 'service'))
                    elif tagval == 'SV_ServiceIdentification':
                        self.identification.append(SV_ServiceIdentification(val))

            self.contentinfo = []
            for contentinfo in md.findall(
                    util.nspath_eval('mdb:contentInfo/mrc:MD_FeatureCatalogueDescription', namespaces)):
                self.contentinfo.append(MD_FeatureCatalogueDescription(contentinfo))
            for contentinfo in md.findall(
                    util.nspath_eval('mdb:contentInfo/mrc:MD_ImageDescription', namespaces)):
                self.contentinfo.append(MD_ImageDescription(contentinfo))

            val = md.find(util.nspath_eval('mdb:distributionInfo/mrd:MD_Distribution', namespaces))

            if val is not None:
                self.distribution = MD_Distribution(val)
            else:
                self.distribution = None

            val = md.find(util.nspath_eval('mdb:dataQualityInfo/mdq:DQ_DataQuality', namespaces))
            if val is not None:
                self.dataquality = DQ_DataQuality(val)
            else:
                self.dataquality = None


    def get_all_contacts(self):
        """ Get all contacts in document

        :returns: list of contacts
        """
        contacts = []
        for ii in self.identification:
            for iic in ii.contact:
                contacts.append(iic)

            for ct in ['creator', 'publisher', 'contributor', 'funder']:
                iict = getattr(ii, ct)
                if iict:
                    contacts.append(iict)

        return list(filter(None, contacts))

    def get_default_locale(self):
        """ Get default lan:PT_Locale based on lan:language

        :returns: default PT_Locale instance or None if not found
        """

        for loc in self.locales:
            if loc.languagecode == self.language:
                return loc
        return None


class PT_Locale(printable):
    """ Process PT_Locale
    """

    def __init__(self, md=None):
        """
        Parses PT_Locale XML subtree

        :param md: PT_Locale etree.Element
        """
        if md is None:
            self.id = None
            self.languagecode = None
            self.charset = None
        else:
            self.id = md.attrib.get('id')
            self.languagecode = md.find(
                util.nspath_eval('lan:language/lan:LanguageCode', namespaces)).attrib.get('codeListValue')
            self.charset = md.find(
                util.nspath_eval('lan:characterEncoding/lan:MD_CharacterSetCode', namespaces)).attrib.get(
                'codeListValue')



class CI_Date(printable):
    """ Process CI_Date
    """
    def __init__(self, md=None):
        """
        Parses CI_Date XML subtree

        :param md: CI_Date etree.Element
        """
        if md is None:
            self.date = None
            self.type = None
        else:
            val = md.find(util.nspath_eval('cit:date/gco:Date', namespaces))
            if val is not None:
                self.date = util.testXMLValue(val)
            else:
                val = md.find(util.nspath_eval('cit:date/gco:DateTime', namespaces))
                if val is not None:
                    self.date = util.testXMLValue(val)
                else:
                    self.date = None

            val = md.find(util.nspath_eval('cit:dateType/cit:CI_DateTypeCode', namespaces))
            self.type = _testCodeListValue(val)


class CI_Responsibility(printable):
    """ Process CI_Responsibility
    """
    def __init__(self, md=None):
        """
        Parses CI_Responsibility XML subtree

        :param md: CI_Responsibility etree.Element
        """
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
            val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:name/gco:CharacterString', namespaces))
            self.name = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:name/gco:CharacterString', namespaces))
            self.organization = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:positionName/gco:CharacterString', namespaces))
            self.position = util.testXMLValue(val)

            # Telephone
            val_list = md.xpath('cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:phone/cit:CI_Telephone[cit:numberType/cit:CI_TelephoneTypeCode/@codeListValue="voice"]/cit:number/gco:CharacterString', namespaces=namespaces)
            if len(val_list) > 0:
                self.phone = util.testXMLValue(val_list[0])

            # Facsimile (Telephone and fax are differentiated by telephone type codes)
            val_list = md.xpath('cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:phone/cit:CI_Telephone[cit:numberType/cit:CI_TelephoneTypeCode/@codeListValue="facsimile"]/cit:number/gco:CharacterString', namespaces=namespaces)
            if len(val_list) > 0:
                self.fax = util.testXMLValue(val_list[0])

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:deliveryPoint/gco:CharacterString',
                namespaces))
            self.address = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:city/gco:CharacterString', namespaces))
            self.city = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:administrativeArea/gco:CharacterString',
                namespaces))
            self.region = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:postalCode/gco:CharacterString',
                namespaces))
            self.postcode = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:country/gco:CharacterString',
                namespaces))
            self.country = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:electronicMailAddress/gco:CharacterString',
                namespaces))
            self.email = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:onlineResource/cit:CI_OnlineResource', namespaces))
            if val is not None:
                self.onlineresource = CI_OnlineResource(val)
            else:
                self.onlineresource = None
            val = md.find(util.nspath_eval('cit:role/cit:CI_RoleCode', namespaces))
            self.role = _testCodeListValue(val)


class Keyword(printable):
    """ Class for complex keywords, with labels and URLs
    """
    def __init__(self, kw=None):
        """
        Parses keyword Element

        :param kw: keyword 'gco:CharacterString' or 'gcx:Anchor' etree.Element
        """
        if kw is None:
            self.name = None
            self.url = None
        else:
            self.name = util.testXMLValue(kw)
            self.url = kw.attrib.get(util.nspath_eval('xlink:href', namespaces))


class MD_Keywords(printable):
    """
    Class for the metadata MD_Keywords element
    """
    def __init__(self, md=None):
        """
        Parses keyword Element

        :param md: keyword etree.Element
        """
        if md is None:
            self.keywords = []
            self.type = None
            self.thesaurus = None
            self.kwdtype_codeList = 'http://standards.iso.org/iso/19115/-3/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode'
        else:
            self.keywords = []
            val = md.findall(util.nspath_eval('mri:keyword/gco:CharacterString', namespaces))
            if len(val) == 0:
                val = md.findall(util.nspath_eval('mri:keyword/gcx:Anchor', namespaces))
            for word in val:
                self.keywords.append(Keyword(word))
            self.type = None
            val = md.find(util.nspath_eval('mri:type/mri:MD_KeywordTypeCode', namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            self.thesaurus = None
            val = md.find(util.nspath_eval('mri:thesaurusName/gco:CharacterString', namespaces))
            if val is not None:
                self.thesaurus = {}

                title = val.find(util.nspath_eval('cit:title/gco:CharacterString', namespaces))
                self.thesaurus['title'] = util.testXMLValue(title)
                self.thesaurus['url'] = None

                if self.thesaurus['title'] is None:  # try gmx:Anchor
                    t = val.find(util.nspath_eval('cit:title/gcx:Anchor', namespaces))
                    if t is not None:
                        self.thesaurus['title'] = util.testXMLValue(t)
                        self.thesaurus['url'] = t.attrib.get(util.nspath_eval('xlink:href', namespaces))

                date_ = val.find(util.nspath_eval('cit:date/cit:CI_Date/cit:date/gco:Date', namespaces))
                self.thesaurus['date'] = util.testXMLValue(date_)

                datetype = val.find(
                    util.nspath_eval('cit:date/cit:CI_Date/cit:dateType/cit:CI_DateTypeCode', namespaces))
                self.thesaurus['datetype'] = util.testXMLAttribute(datetype, 'codeListValue')


class MD_DataIdentification(printable):
    """ Process MD_DataIdentification
    """
    def __init__(self, md=None, identtype=None):
        """
        Parses MD_DataIdentification XML subtree

        :param md: MD_DataIdentification etree.Element
        :param identtype: identitication type e.g. 'dataset' if MD_DataIdentification,
                                                   'service' if MD_ServiceIdentification
        """
        self.aggregationinfo = None
        if md is None:
            self.identtype = None
            self.title = None
            self.alternatetitle = None
            self.uricode = []
            self.uricodespace = []
            self.date = []
            self.datetype = []
            self.uselimitation = []
            self.uselimitation_url = []
            self.accessconstraints = []
            self.classification = []  # Left empty - no legal classification equivalent
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
            self.funder = []
            self.contributor = []
            self.edition = None
            self.abstract = None
            self.abstract_url = None
            self.purpose = None
            self.status = None
            self.graphicoverview = []
            self.contact = []
            self.keywords = []
            self.topiccategory = []
            self.supplementalinformation = None
            self.extent = None
            self.bbox = None
            self.temporalextent_start = None
            self.temporalextent_end = None
            self.spatialrepresentationtype = []
        else:
            self.identtype = identtype
            val = md.find(util.nspath_eval(
                'mri:citation/cit:CI_Citation/cit:title/gco:CharacterString', namespaces))
            self.title = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mri:citation/cit:CI_Citation/cit:alternateTitle/gco:CharacterString', namespaces))
            self.alternatetitle = util.testXMLValue(val)

            self.uricode = []
            for end_tag in ['gco:CharacterString', 'gcx:Anchor']:
                _values = md.findall(util.nspath_eval(
                    f"mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/{end_tag}",
                    namespaces))
                for i in _values:
                    val = util.testXMLValue(i)
                    if val is not None:
                        self.uricode.append(val)

            self.uricodespace = []
            for i in md.findall(util.nspath_eval(
                    'mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:codeSpace/gco:CharacterString',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.uricodespace.append(val)

            self.date = []
            self.datetype = []

            for i in md.findall(util.nspath_eval('mri:citation/cit:CI_Citation/cit:date/cit:CI_Date', namespaces)):
                self.date.append(CI_Date(i))

            self.uselimitation = []
            self.uselimitation_url = []
            uselimit_values = md.findall(util.nspath_eval(
                'mri:resourceConstraints/mco:MD_LegalConstraints/mco:useLimitation/gco:CharacterString>', namespaces))
            for i in uselimit_values:
                val = util.testXMLValue(i)
                if val is not None:
                    self.uselimitation.append(val)

            self.accessconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.accessconstraints.append(val)

            self.classification = [] # Left empty - no legal classification equivalent

            self.otherconstraints = []
            for end_tag in ['gco:CharacterString', 'gcx:Anchor']:
                for i in md.findall(util.nspath_eval(
                        f"mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/{end_tag}",
                        namespaces)):
                    val = util.testXMLValue(i)
                    if val is not None:
                        self.otherconstraints.append(val)

            self.securityconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_SecurityConstraints/mco:classification/mco:MD_ClassificationCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.securityconstraints.append(val)

            self.useconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_LegalConstraints/mco:useConstraints/mco:MD_RestrictionCode',
                    namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.useconstraints.append(val)

            self.denominators = []
            for i in md.findall(util.nspath_eval(
                    'mri:spatialResolution/mri:MD_Resolution/mri:equivalentScale/mri:MD_RepresentativeFraction/mri:denominator/gco:Integer',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.denominators.append(val)

            self.distance = []
            self.uom = []
            for i in md.findall(util.nspath_eval(
                    'mri:spatialResolution/mri:MD_Resolution/mri:distance/gco:Distance', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.distance.append(val)
                self.uom.append(i.get("uom"))

            self.resourcelanguagecode = []
            for i in md.findall(util.nspath_eval('lan:language/lan:LanguageCode', namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.resourcelanguagecode.append(val)

            self.resourcelanguage = []
            for i in md.findall(util.nspath_eval('lan:language/gco:CharacterString', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.resourcelanguage.append(val)

            self.creator = []
            self.publisher = []
            self.contributor = []
            self.funder = []
            for val in md.findall(util.nspath_eval('mri:pointOfContact/cit:CI_Responsibility', namespaces)):
                role = val.find(util.nspath_eval('cit:role/cit:CI_RoleCode', namespaces))
                if role is not None:
                    clv = _testCodeListValue(role)
                    rp = CI_Responsibility(val)
                    if clv == 'originator':
                        self.creator.append(rp)
                    elif clv == 'publisher':
                        self.publisher.append(rp)
                    elif clv == 'author':
                        self.contributor.append(rp)
                    elif clv == 'funder':
                        self.funder.append(rp)

            val = md.find(util.nspath_eval('cit:CI_Citation/cit:edition/gco:CharacterString', namespaces))
            self.edition = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mri:abstract/gco:CharacterString', namespaces))
            self.abstract = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mri:abstract/gcx:Anchor', namespaces))

            self.abstract_url = None
            if val is not None:
                self.abstract = util.testXMLValue(val)
                self.abstract_url = val.attrib.get(util.nspath_eval('xlink:href', namespaces))

            val = md.find(util.nspath_eval('mri:purpose/gco:CharacterString', namespaces))
            self.purpose = util.testXMLValue(val)

            self.status = _testCodeListValue(md.find(util.nspath_eval('mri:status/mri:MD_ProgressCode', namespaces)))

            self.graphicoverview = []
            for val in md.findall(util.nspath_eval(
                    'mri:graphicOverview/mcc:MD_BrowseGraphic/mcc:fileName/gco:CharacterString', namespaces)):
                if val is not None:
                    val2 = util.testXMLValue(val)
                    if val2 is not None:
                        self.graphicoverview.append(val2)

            self.contact = []
            for i in md.findall(util.nspath_eval('mri:pointOfContact/cit:CI_Responsibility', namespaces)):
                o = CI_Responsibility(i)
                self.contact.append(o)

            self.spatialrepresentationtype = []
            for val in md.findall(util.nspath_eval(
                    'mri:spatialRepresentationType/mcc:MD_SpatialRepresentationTypeCode', namespaces)):
                val = util.testXMLAttribute(val, 'codeListValue')
                if val:
                    self.spatialrepresentationtype.append(val)

            self.keywords = []
            for mdkw in md.findall(util.nspath_eval('mri:descriptiveKeywords/mri:MD_Keywords', namespaces)):
                self.keywords.append(MD_Keywords(mdkw))

            self.topiccategory = []
            for i in md.findall(util.nspath_eval('mri:topicCategory/mri:MD_TopicCategoryCode', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.topiccategory.append(val)

            val = md.find(util.nspath_eval('mri:supplementalInformation/gco:CharacterString', namespaces))
            self.supplementalinformation = util.testXMLValue(val)

            # There may be multiple geographicElement, create an extent
            # from the one containing either an EX_GeographicBoundingBox or EX_BoundingPolygon.
            # The schema also specifies an EX_GeographicDescription. This is not implemented yet.
            val = None
            val2 = None
            val3 = None
            extents = md.findall(util.nspath_eval('mri:extent', namespaces))
            for extent in extents:
                # Parse bounding box and vertical extents
                if val is None:
                    for e in extent.findall(util.nspath_eval('gex:EX_Extent/gex:geographicElement', namespaces)):
                        if e.find(util.nspath_eval('gex:EX_GeographicBoundingBox', namespaces)) is not None or \
                                e.find(util.nspath_eval('gex:EX_BoundingPolygon', namespaces)) is not None:
                            val = e
                            break
                    vert_elem = extent.find(util.nspath_eval('gex:EX_Extent/gex:verticalElement', namespaces))
                    self.extent = EX_Extent(val, vert_elem)
                    self.bbox = self.extent.boundingBox  # for backwards compatibility

                # Parse temporal extent begin
                if val2 is None:
                    val2 = extent.find(util.nspath_eval(
                        'gex:EX_Extent/gex:temporalElement/gex:EX_TemporalExtent/gex:extent/gml:TimePeriod/gml:beginPosition',
                        namespaces))
                    self.temporalextent_start = util.testXMLValue(val2)

                # Parse temporal extent end
                if val3 is None:
                    val3 = extent.find(util.nspath_eval(
                        'gex:EX_Extent/gex:temporalElement/gex:EX_TemporalExtent/gex:extent/gml:TimePeriod/gml:endPosition',
                        namespaces))
                    self.temporalextent_end = util.testXMLValue(val3)


class MD_Distributor(printable):
    """ Process MD_Distributor
    """
    def __init__(self, md=None):
        """
        Parses MD_Distributor XML subtree

        :param md: MD_Distributor etree.Element
        """
        if md is None:
            self.contact = None
            self.online = []
        else:
            self.contact = None
            val = md.find(util.nspath_eval(
                'mrd:MD_Distributor/mrd:distributorContact/cit:CI_Responsibility', namespaces))
            if val is not None:
                self.contact = CI_Responsibility(val)

            self.online = []

            for ol in md.findall(util.nspath_eval(
                    'mrd:MD_Distributor/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions/cit:onLine/cit:CI_OnlineResource',
                    namespaces)):
                self.online.append(CI_OnlineResource(ol))


class MD_Distribution(printable):
    """ Process MD_Distribution
    """
    def __init__(self, md=None):
        """
        Parses MD_Distribution XML subtree

        :param md: MD_Distribution etree.Element
        """
        if md is None:
            self.format = None
            self.version = None
            self.distributor = []
            self.online = []
        else:
            val = md.find(util.nspath_eval(
                'mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:title/gco:CharacterString', namespaces))
            self.format = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:edition/gco:CharacterString', namespaces))
            self.version = util.testXMLValue(val)

            self.distributor = []
            for dist in md.findall(util.nspath_eval('mrd:distributor', namespaces)):
                self.distributor.append(MD_Distributor(dist))

            self.online = []

            for ol in md.findall(util.nspath_eval(
                    'mrd:transferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource',
                    namespaces)):
                self.online.append(CI_OnlineResource(ol))


class DQ_DataQuality(printable):
    """ Process DQ_DataQuality
    """
    def __init__(self, md=None):
        """
        Parses DQ_DataQuality XML subtree

        :param md: DQ_DataQuality etree.Element
        """
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
            val = md.find(util.nspath_eval(
                'mdq:evaluationProcedure/cit:CI_Citation/cit:title/gco:CharacterString', namespaces))
            self.conformancetitle = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mdq:evaluationProcedure/cit:CI_Citation/cit:date', namespaces))
            self.conformancedate = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mdq:evaluationProcedure/cit:CI_Citation/cit:date/cit:CI_DateTypeCode', namespaces))
            self.conformancedatetype = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mdq:result/mdq:DQ_QuantitativeResult/mdq:value/gco:Record', namespaces))
            self.conformancedegree = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mdb:resourceLineage/mrl:LI_Lineage/mrl:statement/gco:CharacterString', namespaces))
            self.lineage = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:resourceLineage/mrl:LI_Lineage/mrl:statement/gcx:Anchor', namespaces))
            if val is not None:
                self.lineage = util.testXMLValue(val)
                self.lineage_url = val.attrib.get(util.nspath_eval('xlink:href', namespaces))

            val = md.find(util.nspath_eval(
                'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:title/gco:CharacterString',
                namespaces))
            self.specificationtitle = util.testXMLValue(val)

            self.specificationdate = []
            for i in md.findall(util.nspath_eval(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:date/cit:CI_Date',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.specificationdate.append(val)


class SV_ServiceIdentification(MD_DataIdentification, printable):
    """ Process SV_ServiceIdentification
    """
    def __init__(self, md=None):
        """
        Parses SV_ServiceIdentification XML subtree

        :param md: SV_ServiceIdentification etree.Element
        """
        super().__init__(md, 'service')

        if md is None:
            self.type = None
            self.version = None
            self.fees = None
            self.couplingtype = None
            self.operations = []
            self.operateson = []
        else:
            val = md.xpath('srv:serviceType/*[self::gco:LocalName or self::gco:ScopedName]', namespaces=namespaces)
            if len(val) > 0:
                self.type = util.testXMLValue(val[0])

            val = md.find(util.nspath_eval('srv:serviceTypeVersion/gco:CharacterString', namespaces))
            self.version = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'srv:accessProperties/mrd:MD_StandardOrderProcess/mrd:fees/gco:CharacterString', namespaces))
            self.fees = util.testXMLValue(val)

            self.couplingtype = _testCodeListValue(md.find(util.nspath_eval(
                'srv:couplingType/srv:SV_CouplingType', namespaces)))

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
                    tmp3 = d.find(util.nspath_eval('cit:CI_OnlineResource', namespaces))
                    tmp['connectpoint'].append(CI_OnlineResource(tmp3))
                self.operations.append(tmp)

            self.operateson = []

            for i in md.findall(util.nspath_eval('srv:operatesOn', namespaces)):
                tmp = {}
                tmp['uuidref'] = i.attrib.get('uuidref')
                tmp['href'] = i.attrib.get(util.nspath_eval('xlink:href', namespaces))
                tmp['title'] = i.attrib.get(util.nspath_eval('xlink:title', namespaces))
                self.operateson.append(tmp)


class CI_OnlineResource(printable):
    """ Process CI_OnlineResource
    """
    def __init__(self, md=None):
        """
        Parses CI_OnlineResource XML subtree

        :param md: CI_OnlineResource etree.Element
        """
        if md is None:
            self.url = None
            self.protocol = None
            self.name = None
            self.description = None
            self.function = None
        else:
            val = md.find(util.nspath_eval('cit:linkage/gco:CharacterString', namespaces))
            self.url = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:protocol/gco:CharacterString', namespaces))
            self.protocol = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:name/gco:CharacterString', namespaces))
            self.name = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:description/gco:CharacterString', namespaces))
            self.description = util.testXMLValue(val)

            self.function = _testCodeListValue(md.find(util.nspath_eval(
                'cit:function/cit:CI_OnLineFunctionCode', namespaces)))


class EX_GeographicBoundingBox(printable):
    """ Process gex:EX_GeographicBoundingBox
    """
    def __init__(self, md=None):
        """
        Parses EX_GeographicBoundingBox XML subtree

        :param md: EX_GeographicBoundingBox etree.Element
        """
        if md is None:
            self.minx = None
            self.maxx = None
            self.miny = None
            self.maxy = None
        else:
            val = md.find(util.nspath_eval('gex:westBoundLongitude/gco:Decimal', namespaces))
            self.minx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:eastBoundLongitude/gco:Decimal', namespaces))
            self.maxx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:southBoundLatitude/gco:Decimal', namespaces))
            self.miny = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:northBoundLatitude/gco:Decimal', namespaces))
            self.maxy = util.testXMLValue(val)


class EX_Polygon(printable):
    """ Process gml32:Polygon
    """
    def __init__(self, md=None):
        """
        Parses EX_Polygon XML subtree

        :param md: EX_Polygon etree.Element
        """
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
        """ Get coordinates for gml coordinate ring

        :param linear_ring: etree.Element position list
        :returns: coordinate list of float tuples
        """
        coordinates = []
        positions = linear_ring.findall(util.nspath_eval('gml32:pos', namespaces))
        for pos in positions:
            tokens = pos.text.split()
            coords = tuple([float(t) for t in tokens])
            coordinates.append(coords)
        return coordinates


class EX_BoundingPolygon(printable):
    """ Process EX_BoundingPolygon
    """
    def __init__(self, md=None):
        """
        Parses EX_BoundingPolygon XML subtree

        :param md: EX_BoundingPolygon etree.Element
        """
        if md is None:
            self.is_extent = None
            self.polygons = []
        else:
            val = md.find(util.nspath_eval('gex:extentTypeCode', namespaces))
            self.is_extent = util.testXMLValue(val)

            md_polygons = md.findall(util.nspath_eval('gex:polygon', namespaces))

            self.polygons = []
            for val in md_polygons:
                self.polygons.append(EX_Polygon(val))


class EX_Extent(printable):
    """ Process EX_Extent
    """
    def __init__(self, md=None, vert_elem=None):
        """
        Parses EX_Extent XML subtree

        :param md: EX_Extent etree.Element
        :param vert_elem: vertical extent 'gex:verticalElement' etree.Element
        """
        self.boundingBox = None
        self.boundingPolygon = None
        self.description_code = None
        self.vertExtMin = None
        self.vertExtMax = None
        if md is not None:
            # Parse bounding box
            bboxElement = md.find(util.nspath_eval('gex:EX_GeographicBoundingBox', namespaces))
            if bboxElement is not None:
                self.boundingBox = EX_GeographicBoundingBox(bboxElement)

            polygonElement = md.find(util.nspath_eval('gex:EX_BoundingPolygon', namespaces))
            if polygonElement is not None:
                self.boundingPolygon = EX_BoundingPolygon(polygonElement)

            code = md.find(util.nspath_eval(
                'gex:EX_GeographicDescription/gex:geographicIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString',
                namespaces))
            self.description_code = util.testXMLValue(code)

        # Parse vertical extent
        if vert_elem is not None:
            # Get vertical extent max
            vertext_max = vert_elem.find(util.nspath_eval(
                'gex:EX_VerticalExtent/gex:maximumValue/gco:Real',
                namespaces))
            self.vertExtMax = util.testXMLValue(vertext_max)

            # Get vertical extent min
            vertext_min = vert_elem.find(util.nspath_eval(
                'gex:EX_VerticalExtent/gex:minimumValue/gco:Real',
                namespaces))
            self.vertExtMin = util.testXMLValue(vertext_min)


class MD_ReferenceSystem(printable):
    """ Process MD_ReferenceSystem
    """
    def __init__(self, md=None):
        """
        Parses MD_ReferenceSystem XML subtree

        :param md: MD_ReferenceSystem etree.Element
        """
        if md is None:
            self.code = None
            self.codeSpace = None
            self.version = None
        else:
            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', namespaces))
            if val is not None:
                self.code = util.testXMLValue(val)
            else:
                val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gcx:Anchor', namespaces))
                if val is not None:
                    self.code = util.testXMLValue(val)
                else:
                    self.code = None

            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:codeSpace/gco:CharacterString', namespaces))
            if val is not None:
                self.codeSpace = util.testXMLValue(val)
            else:
                self.codeSpace = None

            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:version/gco:CharacterString', namespaces))
            if val is not None:
                self.version = util.testXMLValue(val)
            else:
                self.version = None


def _testCodeListValue(elpath):
    """ Get gco:CodeListValue_Type attribute, else get text content

    :param elpath: Element path
    :returns: 'codeListValue' attribute of Element or text value or None if elpath is None
    """
    if elpath is not None:  # try to get @codeListValue
        val = util.testXMLValue(elpath.attrib.get('codeListValue'), True)
        if val is not None:
            return val
        # see if there is element text
        return util.testXMLValue(elpath)

    return None


class MD_FeatureCatalogueDescription(printable):
    """Process mrc:MD_FeatureCatalogueDescription
    """
    def __init__(self, fcd=None):
        """
        Parses MD_FeatureCatalogueDescription XML subtree

        :param fcd: MD_FeatureCatalogueDescription etree.Element
        """
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
            comp = fcd.find(util.nspath_eval('mrc:complianceCode/gco:Boolean', namespaces))
            val = util.testXMLValue(comp)
            if val is not None:
                self.compliancecode = util.getTypedValue('boolean', val)

            self.language = []
            for i in fcd.findall(util.nspath_eval('lan:language/gco:CharacterString', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.language.append(val)

            self.includedwithdataset = None
            comp = fcd.find(util.nspath_eval('mrc:includedWithDataset/gco:Boolean', namespaces))
            val = util.testXMLValue(comp)
            if val is not None:
                self.includedwithdataset = util.getTypedValue('boolean', val)

            self.featuretypenames = []
            for i in fcd.findall(util.nspath_eval('mrc:featureTypes/mrc:MD_FeatureTypeInfo/mrc:featureTypeName/gml:CodeType', namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.featuretypenames.append(val)

            # Gather feature catalogue titles
            self.featurecatalogues = []
            for cit in fcd.findall(util.nspath_eval(
                    'mrc:featureCatalogueCitation/cit:CI_Citation/cit:title/gco:CharacterString', namespaces)):
                val = util.testXMLValue(cit)
                if val is not None:
                    self.featurecatalogues.append(val)

class MD_ImageDescription(printable):
    """Process mrc:MD_ImageDescription
    """
    def __init__(self, img_desc=None):
        """
        Parses MD_ImageDescription XML subtree

        :param img_desc: MD_ImageDescription etree.Element
        """
        self.type = 'image'
        self.bands = []

        if img_desc is None:
            self.attribute_description = None
            self.cloud_cover = None
            self.processing_level = None
        else:
            val = img_desc.find(util.nspath_eval('mrc:attributeDescription/gco:RecordType', namespaces))
            self.attribute_description = util.testXMLValue(val)

            val = img_desc.find(util.nspath_eval('mrc:attributeGroup/mrc:MD_CoverageContentTypeCode', namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            val = img_desc.find(util.nspath_eval('mrc:cloudCoverPercentage/gco:Real', namespaces))
            self.cloud_cover = util.testXMLValue(val)

            val = img_desc.find(util.nspath_eval(
                'mrc:processingLevelCode/mcc:MD_Identifier/mcc:code/gco:CharacterString', namespaces))
            self.processing_level = util.testXMLValue(val)

            for i in img_desc.findall(util.nspath_eval('mrc:attributeGroup/mrc:MD_Band', namespaces)):
                bid = util.testXMLAttribute(i, 'id')
                self.bands.append(MD_Band(i, bid))


class MD_Band(printable):
    """Process mrc:MD_Band
    """
    def __init__(self, band, band_id=None):
        """
        Parses MD_Band XML subtree

        :param band: MD_Band etree.Element
        :param band_id: optional id attribute
        """
        if band is None:
            self.id = None
            self.units = None
            self.min = None
            self.max = None
        else:
            self.id = band_id

            val = band.find(util.nspath_eval('mrc:units/gml:UnitDefinition/gml:identifier', namespaces))
            self.units = util.testXMLValue(val)

            val = band.find(util.nspath_eval('mrc:minValue/gco:Real', namespaces))
            self.min = util.testXMLValue(val)

            val = band.find(util.nspath_eval('mrc:maxValue/gco:Real', namespaces))
            self.max = util.testXMLValue(val)
