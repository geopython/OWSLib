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
    from owslib.iso3 import MD_Metadata

    exml = etree.fromstring(xml_bytes)
    mdb = MD_Metadata(exml)
"""

from owslib.etree import etree
from owslib import util


# ISO 19115 Part 3 XML namespaces
NAMESPACES_V2 = {
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

NAMESPACES_V1 =  {
        "xsi":"http://www.w3.org/2001/XMLSchema-instance",
        "cat":"http://standards.iso.org/iso/19115/-3/cat/1.0",
        "cit":"http://standards.iso.org/iso/19115/-3/cit/1.0",
        "gcx":"http://standards.iso.org/iso/19115/-3/gcx/1.0",
        "gex":"http://standards.iso.org/iso/19115/-3/gex/1.0",
        "gfc":"http://standards.iso.org/iso/19110/gfc/1.1",
        "lan":"http://standards.iso.org/iso/19115/-3/lan/1.0",
        "srv":"http://standards.iso.org/iso/19115/-3/srv/2.0",
        "mac":"http://standards.iso.org/iso/19115/-3/mac/1.0",
        "mas":"http://standards.iso.org/iso/19115/-3/mas/1.0",
        "mcc":"http://standards.iso.org/iso/19115/-3/mcc/1.0",
        "mco":"http://standards.iso.org/iso/19115/-3/mco/1.0",
        "mda":"http://standards.iso.org/iso/19115/-3/mda/1.0",
        "mdb":"http://standards.iso.org/iso/19115/-3/mdb/1.0",
        "mdt":"http://standards.iso.org/iso/19115/-3/mdt/1.0",
        "mex":"http://standards.iso.org/iso/19115/-3/mex/1.0",
        "mrl":"http://standards.iso.org/iso/19115/-3/mrl/1.0",
        "mds":"http://standards.iso.org/iso/19115/-3/mds/1.0",
        "mmi":"http://standards.iso.org/iso/19115/-3/mmi/1.0",
        "mpc":"http://standards.iso.org/iso/19115/-3/mpc/1.0",
        "mrc":"http://standards.iso.org/iso/19115/-3/mrc/1.0",
        "mrd":"http://standards.iso.org/iso/19115/-3/mrd/1.0",
        "mri":"http://standards.iso.org/iso/19115/-3/mri/1.0",
        "mrs":"http://standards.iso.org/iso/19115/-3/mrs/1.0",
        "msr":"http://standards.iso.org/iso/19115/-3/msr/1.0",
        "mdq":"http://standards.iso.org/iso/19157/-2/mdq/1.0",
        "dqc":"http://standards.iso.org/iso/19157/-2/dqc/1.0",
        "gco":"http://standards.iso.org/iso/19115/-3/gco/1.0",
        "gml":"http://www.opengis.net/gml/3.2",
        "xlink":"http://www.w3.org/1999/xlink"
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
        self.namespaces = NAMESPACES_V2
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

           # Test mdb version
            if md.find(util.nspath_eval('mdb:metadataIdentifier', NAMESPACES_V2)) is None and \
                    md.find(util.nspath_eval('mdb:metadataIdentifier', NAMESPACES_V1)) is not None:
                self.namespaces = NAMESPACES_V1

            val = md.find(util.nspath_eval('mdb:metadataIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', self.namespaces))
            self.identifier = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:parentMetadata/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', self.namespaces))
            self.parentidentifier = util.testXMLValue(val)

            val = md.find(util.nspath_eval('lan:language/gco:CharacterString', self.namespaces))
            self.language = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', self.namespaces))
            self.dataseturi = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:defaultLocale/lan:PT_Locale/lan:language/lan:LanguageCode', self.namespaces))
            self.languagecode = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(util.nspath_eval('mdb:dateInfo/cit:CI_Date/cit:date/gco:DateTime', self.namespaces))
            self.datestamp = util.testXMLValue(val)

            val = md.find(
                util.nspath_eval('mdb:defaultLocale/lan:PT_Locale/lan:characterEncoding/lan:MD_CharacterSetCode', self.namespaces))
            self.charset = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(
                util.nspath_eval('mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode', self.namespaces))
            self.hierarchy = util.testXMLAttribute(val, 'codeListValue')

            self.contact = []
            for i in md.findall(util.nspath_eval('mdb:contact/cit:CI_Responsibility', self.namespaces)):
                o = CI_Responsibility(self.namespaces, i)
                self.contact.append(o)

            self.datetimestamp = self.datestamp

            val = md.find(util.nspath_eval('mdb:metadataStandard/cit:CI_Citation/cit:title/gco:CharacterString', self.namespaces))
            self.stdname = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mdb:metadataStandard/cit:CI_Citation/cit:edition/gco:CharacterString', self.namespaces))
            self.stdver = util.testXMLValue(val)

            self.locales = []
            for i in md.findall(util.nspath_eval('mdb:defaultLocale/lan:PT_Locale', self.namespaces)):
                self.locales.append(PT_Locale(self.namespaces, i))

            val = md.find(util.nspath_eval('mdb:referenceSystemInfo/mrs:MD_ReferenceSystem', self.namespaces))
            if val is not None:
                self.referencesystem = MD_ReferenceSystem(self.namespaces, val)
            else:
                self.referencesystem = None

            self.identification = []

            for idinfo in md.findall(util.nspath_eval('mdb:identificationInfo', self.namespaces)):
                if len(idinfo) > 0:
                    val = list(idinfo)[0]
                    tagval = util.xmltag_split(val.tag)
                    if tagval == 'MD_DataIdentification':
                        self.identification.append(MD_DataIdentification(self.namespaces, val, 'dataset'))
                    elif tagval == 'MD_ServiceIdentification':
                        self.identification.append(MD_DataIdentification(self.namespaces, val, 'service'))
                    elif tagval == 'SV_ServiceIdentification':
                        self.identification.append(SV_ServiceIdentification(self.namespaces, val))

            self.contentinfo = []
            for contentinfo in md.findall(
                    util.nspath_eval('mdb:contentInfo/mrc:MD_FeatureCatalogueDescription', self.namespaces)):
                self.contentinfo.append(MD_FeatureCatalogueDescription(self.namespaces, contentinfo))
            for contentinfo in md.findall(
                    util.nspath_eval('mdb:contentInfo/mrc:MD_ImageDescription', self.namespaces)):
                self.contentinfo.append(MD_ImageDescription(self.namespaces, contentinfo))
            for contentinfo in md.findall(
                    util.nspath_eval('mdb:contentInfo/mrc:MD_FeatureCatalogue/mrc:featureCatalogue/gfc:FC_FeatureCatalogue',
                                     self.namespaces)):
                self.contentinfo.append(FC_FeatureCatalogue(self.namespaces, contentinfo))

            val = md.find(util.nspath_eval('mdb:distributionInfo/mrd:MD_Distribution', self.namespaces))

            if val is not None:
                self.distribution = MD_Distribution(self.namespaces, val)
            else:
                self.distribution = None

            val = md.find(util.nspath_eval('mdb:dataQualityInfo/mdq:DQ_DataQuality', self.namespaces))
            if val is not None:
                self.dataquality = DQ_DataQuality(self.namespaces, val)
            else:
                self.dataquality = None

    @staticmethod
    def find_start(doc):
        """ Tests for valid ISO 19115 Part 3 XML and returns the starting tag

        :param doc: lxml Element object
        :returns: 'mdb:MD_Metadata' lxml Element object
        """
        mtags = doc.xpath("//mdb:MD_Metadata", namespaces=NAMESPACES_V2)
        if len(mtags) > 0:
            return mtags[0]
        mtags = doc.xpath("//mdb:MD_Metadata", namespaces=NAMESPACES_V1)
        if len(mtags) > 0:
            return mtags[0]
        return None

    @staticmethod
    def handles(outputschema):
        """ Returns True iff the outputschema is handled by this class

        :param outputschema: outputschema parameter string
        :returns: True iff the outputschema is handled by this class
        """
        return outputschema == NAMESPACES_V1['mdb'] or \
               outputschema == NAMESPACES_V2['mdb']

    @staticmethod
    def find_ids(elemtree):
        """ Finds identifer strings and outer 'mdb:MD_Metadata' Elements

        :param elemtree: lxml.ElementTree to search in
        :returns: a list of tuples (id string, 'mdb:MD_Metadata' lxml.Element)
        """
        for ns in [NAMESPACES_V2, NAMESPACES_V1]:
            elems = elemtree.findall('.//' + util.nspath_eval('mdb:MD_Metadata', ns))
            if len(elems) > 0:
                ret_list = []
                for i in elems:
                    val = i.find(util.nspath_eval('mdb:metadataIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', NAMESPACES_V2))
                    ret_list.append((i, util.testXMLValue(val)))
                return ret_list
        return []

    def get_all_contacts(self):
        """ Get all contacts in identification part of document

        :returns: list of CI_Responsibility contacts
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

    def __init__(self, namespaces, md=None):
        """
        Parses PT_Locale XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: PT_Locale etree.Element
        """
        self.namespaces = namespaces

        self.id = None
        self.languagecode = None
        self.charset = None

        if md is not None:
            try:
                self.id = md.attrib.get('id')
            except AttributeError:
                pass

            try:
                self.languagecode = md.find(
                    util.nspath_eval('lan:language/lan:LanguageCode', self.namespaces)).attrib.get('codeListValue')
            except AttributeError:
                pass

            try:
                self.charset = md.find(
                    util.nspath_eval('lan:characterEncoding/lan:MD_CharacterSetCode', self.namespaces)).attrib.get(
                    'codeListValue')
            except AttributeError:
                pass


class CI_Date(printable):
    """ Process CI_Date
    """
    def __init__(self, namespaces, md=None):
        """
        Parses CI_Date XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: CI_Date etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.date = None
            self.type = None
        else:
            val = md.find(util.nspath_eval('cit:date/gco:Date', self.namespaces))
            if val is not None:
                self.date = util.testXMLValue(val)
            else:
                val = md.find(util.nspath_eval('cit:date/gco:DateTime', self.namespaces))
                if val is not None:
                    self.date = util.testXMLValue(val)
                else:
                    self.date = None

            val = md.find(util.nspath_eval('cit:dateType/cit:CI_DateTypeCode', self.namespaces))
            self.type = _testCodeListValue(val)


class CI_Responsibility(printable):
    """ Process CI_Responsibility
    """
    def __init__(self, namespaces, md=None):
        """
        Parses CI_Responsibility XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: CI_Responsibility etree.Element
        """
        self.namespaces = namespaces
        self.phone = None
        self.fax = None
        if md is None:
            self.name = None
            self.organization = None
            self.position = None
            self.address = None
            self.city = None
            self.region = None
            self.postcode = None
            self.country = None
            self.email = None
            self.onlineresource = None
            self.role = None
        else:
            # Individual name
            val = md.find(util.nspath_eval('cit:party/cit:CI_Individual/cit:name/gco:CharacterString', self.namespaces))
            self.name = util.testXMLValue(val)

            # Individual within organisation name
            if self.name is None:
                val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:name/gco:CharacterString', self.namespaces))
                self.name = util.testXMLValue(val)

            # Organisation name
            val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:name/gco:CharacterString', self.namespaces))
            self.organization = util.testXMLValue(val)

            # Individual within organisation position
            val = md.find(util.nspath_eval('cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:positionName/gco:CharacterString', self.namespaces))
            self.position = util.testXMLValue(val)

            # Organisation telephone
            val_list = md.xpath('cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:phone/cit:CI_Telephone[cit:numberType/cit:CI_TelephoneTypeCode/@codeListValue="voice"]/cit:number/gco:CharacterString', namespaces=self.namespaces)
            if len(val_list) > 0:
                self.phone = util.testXMLValue(val_list[0])

            # Facsimile (Telephone and fax are differentiated by telephone type codes)
            val_list = md.xpath('cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:phone/cit:CI_Telephone[cit:numberType/cit:CI_TelephoneTypeCode/@codeListValue="facsimile"]/cit:number/gco:CharacterString', namespaces=self.namespaces)
            if len(val_list) > 0:
                self.fax = util.testXMLValue(val_list[0])

            # Organisation address
            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:deliveryPoint/gco:CharacterString',
                self.namespaces))
            self.address = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:city/gco:CharacterString', self.namespaces))
            self.city = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:administrativeArea/gco:CharacterString',
                self.namespaces))
            self.region = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:postalCode/gco:CharacterString',
                self.namespaces))
            self.postcode = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:country/gco:CharacterString',
                self.namespaces))
            self.country = util.testXMLValue(val)

            # Organisation email
            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:address/cit:CI_Address/cit:electronicMailAddress/gco:CharacterString',
                self.namespaces))
            self.email = util.testXMLValue(val)

            # Organisation online resources
            val = md.find(util.nspath_eval(
                'cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact/cit:onlineResource/cit:CI_OnlineResource', self.namespaces))
            if val is not None:
                self.onlineresource = CI_OnlineResource(self.namespaces, val)
            else:
                self.onlineresource = None
            val = md.find(util.nspath_eval('cit:role/cit:CI_RoleCode', self.namespaces))
            self.role = _testCodeListValue(val)


class Keyword(printable):
    """ Class for complex keywords, with labels and URLs
    """
    def __init__(self, namespaces, kw=None):
        """
        Parses keyword Element

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param kw: keyword 'gco:CharacterString' or 'gcx:Anchor' etree.Element
        """
        self.namespaces = namespaces
        if kw is None:
            self.name = None
            self.url = None
        else:
            self.name = util.testXMLValue(kw)
            self.url = kw.attrib.get(util.nspath_eval('xlink:href', self.namespaces))


class MD_Keywords(printable):
    """
    Class for the metadata MD_Keywords element
    """
    def __init__(self, namespaces, md=None):
        """
        Parses keyword Element

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: keyword etree.Element
        """
        self.namespaces = namespaces
        self.thesaurus = None
        self.keywords = []
        self.type = None
        self.kwdtype_codeList = 'http://standards.iso.org/iso/19115/-3/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode'

        if md is not None:
            val = md.findall(util.nspath_eval('mri:keyword/gco:CharacterString', self.namespaces))
            if len(val) == 0:
                val = md.findall(util.nspath_eval('mri:keyword/gcx:Anchor', self.namespaces))
            for word in val:
                self.keywords.append(Keyword(self.namespaces, word))

            val = md.find(util.nspath_eval('mri:type/mri:MD_KeywordTypeCode', self.namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            cit = md.find(util.nspath_eval('mri:thesaurusName/cit:CI_Citation', self.namespaces))
            if cit is not None:
                self.thesaurus = {}

                title = cit.find(util.nspath_eval('cit:title/gco:CharacterString', self.namespaces))
                self.thesaurus['title'] = util.testXMLValue(title)
                self.thesaurus['url'] = None

                if self.thesaurus['title'] is None:  # try gmx:Anchor
                    t = cit.find(util.nspath_eval('cit:title/gcx:Anchor', self.namespaces))
                    if t is not None:
                        self.thesaurus['title'] = util.testXMLValue(t)
                        self.thesaurus['url'] = t.attrib.get(util.nspath_eval('xlink:href', self.namespaces))

                date_ = cit.find(util.nspath_eval('cit:date/cit:CI_Date/cit:date/gco:Date', self.namespaces))
                self.thesaurus['date'] = util.testXMLValue(date_)

                datetype = cit.find(
                    util.nspath_eval('cit:date/cit:CI_Date/cit:dateType/cit:CI_DateTypeCode', self.namespaces))
                self.thesaurus['datetype'] = util.testXMLAttribute(datetype, 'codeListValue')

class MD_DataIdentification(printable):
    """ Process MD_DataIdentification
    """
    def __init__(self, namespaces, md=None, identtype=None):
        """
        Parses MD_DataIdentification XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: MD_DataIdentification etree.Element
        :param identtype: identitication type e.g. 'dataset' if MD_DataIdentification,
                                                   'service' if MD_ServiceIdentification
        """
        self.namespaces = namespaces
        self.aggregationinfo = None
        self.bbox = None
        self.temporalextent_start = None
        self.temporalextent_end = None
        self.extent = None
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
            self.spatialrepresentationtype = []
        else:
            # Title
            self.identtype = identtype
            val = md.find(util.nspath_eval(
                'mri:citation/cit:CI_Citation/cit:title/gco:CharacterString', self.namespaces))
            self.title = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mri:citation/cit:CI_Citation/cit:alternateTitle/gco:CharacterString', self.namespaces))
            self.alternatetitle = util.testXMLValue(val)

            # Identifier
            self.uricode = []
            for end_tag in ['gco:CharacterString', 'gcx:Anchor']:
                _values = md.findall(util.nspath_eval(
                    f"mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/{end_tag}",
                    self.namespaces))
                for i in _values:
                    val = util.testXMLValue(i)
                    if val is not None:
                        self.uricode.append(val)

            self.uricodespace = []
            for i in md.findall(util.nspath_eval(
                    'mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:codeSpace/gco:CharacterString',
                    self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.uricodespace.append(val)

            # Date
            self.date = []
            self.datetype = []

            for i in md.findall(util.nspath_eval('mri:citation/cit:CI_Citation/cit:date/cit:CI_Date', self.namespaces)):
                self.date.append(CI_Date(self.namespaces, i))

            # Use Limitation
            self.uselimitation = []
            self.uselimitation_url = []
            uselimit_values = md.findall(util.nspath_eval(
                'mri:resourceConstraints/mco:MD_LegalConstraints/mco:useLimitation/gco:CharacterString', self.namespaces))
            for i in uselimit_values:
                val = util.testXMLValue(i)
                if val is not None:
                    self.uselimitation.append(val)

            # Access constraints
            self.accessconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode',
                    self.namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.accessconstraints.append(val)

            # Classification
            self.classification = [] # Left empty - no legal classification equivalent

            # Other constraints
            self.otherconstraints = []
            for end_tag in ['gco:CharacterString', 'gcx:Anchor']:
                for i in md.findall(util.nspath_eval(
                        f"mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/{end_tag}",
                        self.namespaces)):
                    val = util.testXMLValue(i)
                    if val is not None:
                        self.otherconstraints.append(val)

            # Security constraints
            self.securityconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_SecurityConstraints/mco:classification/mco:MD_ClassificationCode',
                    self.namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.securityconstraints.append(val)

            # Use constraints
            self.useconstraints = []
            for i in md.findall(util.nspath_eval(
                    'mri:resourceConstraints/mco:MD_LegalConstraints/mco:useConstraints/mco:MD_RestrictionCode',
                    self.namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.useconstraints.append(val)

            # Spatial resolution denominators
            self.denominators = []
            for i in md.findall(util.nspath_eval(
                    'mri:spatialResolution/mri:MD_Resolution/mri:equivalentScale/mri:MD_RepresentativeFraction/mri:denominator/gco:Integer',
                    self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.denominators.append(val)

            # Spatial resolution distance and units of measure
            self.distance = []
            self.uom = []
            for i in md.findall(util.nspath_eval(
                    'mri:spatialResolution/mri:MD_Resolution/mri:distance/gco:Distance', self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.distance.append(val)
                self.uom.append(i.get("uom"))

            # Language code
            self.resourcelanguagecode = []
            for i in md.findall(util.nspath_eval('mri:defaultLocale/lan:PT_Locale/lan:language/lan:LanguageCode', self.namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.resourcelanguagecode.append(val)

            # Language
            self.resourcelanguage = []
            for i in md.findall(util.nspath_eval('mri:defaultLocale/lan:PT_Locale/lan:language/gco:CharacterString', self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.resourcelanguage.append(val)

            self.creator = []
            self.publisher = []
            self.contributor = []
            self.funder = []
            # Extract roles from point of contact for resource
            for val in md.findall(util.nspath_eval('mri:pointOfContact/cit:CI_Responsibility', self.namespaces)):
                role = val.find(util.nspath_eval('cit:role/cit:CI_RoleCode', self.namespaces))
                if role is not None:
                    clv = _testCodeListValue(role)
                    rp = CI_Responsibility(self.namespaces, val)
                    # Creator
                    if clv in ['originator', 'principalInvestigator', 'author']:
                        self.creator.append(rp)
                    # Publisher
                    elif clv == 'publisher':
                        self.publisher.append(rp)
                    # Contributor
                    elif clv in ['collaborator', 'coAuthor', 'contributor', 'editor']:
                        self.contributor.append(rp)

            # Edition
            val = md.find(util.nspath_eval('cit:CI_Citation/cit:edition/gco:CharacterString', self.namespaces))
            self.edition = util.testXMLValue(val)

            # Extract roles from responsible party for resource
            for val in md.findall(util.nspath_eval('mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility', self.namespaces)):
                role = val.find(util.nspath_eval('cit:role/cit:CI_RoleCode', self.namespaces))
                if role is not None:
                    clv = _testCodeListValue(role)
                    rp = CI_Responsibility(self.namespaces, val)
                    # Creator
                    if clv in ['originator', 'principalInvestigator', 'author']:
                        self.creator.append(rp)
                    # Publisher
                    elif clv == 'publisher':
                        self.publisher.append(rp)
                    # Contributor
                    elif clv in ['collaborator', 'coAuthor', 'contributor', 'processor', 'editor']:
                        self.contributor.append(rp)
                    # Funder
                    elif clv == 'funder':
                        self.funder.append(rp)

            # Abstract
            val = md.find(util.nspath_eval('mri:abstract/gco:CharacterString', self.namespaces))
            self.abstract = util.testXMLValue(val)

            val = md.find(util.nspath_eval('mri:abstract/gcx:Anchor', self.namespaces))

            self.abstract_url = None
            if val is not None:
                self.abstract = util.testXMLValue(val)
                self.abstract_url = val.attrib.get(util.nspath_eval('xlink:href', self.namespaces))

            # Purpose
            val = md.find(util.nspath_eval('mri:purpose/gco:CharacterString', self.namespaces))
            self.purpose = util.testXMLValue(val)

            # Status
            self.status = _testCodeListValue(md.find(util.nspath_eval('mri:status/mri:MD_ProgressCode', self.namespaces)))

            # Graphic overview
            self.graphicoverview = []
            for val in md.findall(util.nspath_eval(
                    'mri:graphicOverview/mcc:MD_BrowseGraphic/mcc:fileName/gco:CharacterString', self.namespaces)):
                if val is not None:
                    val2 = util.testXMLValue(val)
                    if val2 is not None:
                        self.graphicoverview.append(val2)

            # Point of Contact
            self.contact = []
            for i in md.findall(util.nspath_eval('mri:pointOfContact/cit:CI_Responsibility', self.namespaces)):
                o = CI_Responsibility(self.namespaces, i)
                self.contact.append(o)

            # Spatial repreentation type
            self.spatialrepresentationtype = []
            for val in md.findall(util.nspath_eval(
                    'mri:spatialRepresentationType/mcc:MD_SpatialRepresentationTypeCode', self.namespaces)):
                val = util.testXMLAttribute(val, 'codeListValue')
                if val:
                    self.spatialrepresentationtype.append(val)

            # Keywords
            self.keywords = []
            for mdkw in md.findall(util.nspath_eval('mri:descriptiveKeywords/mri:MD_Keywords', self.namespaces)):
                self.keywords.append(MD_Keywords(self.namespaces, mdkw))

            # Topic category
            self.topiccategory = []
            for i in md.findall(util.nspath_eval('mri:topicCategory/mri:MD_TopicCategoryCode', self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.topiccategory.append(val)

            # Supplamental information
            val = md.find(util.nspath_eval('mri:supplementalInformation/gco:CharacterString', self.namespaces))
            self.supplementalinformation = util.testXMLValue(val)

            # There may be multiple geographicElement, create an extent
            # from the one containing either an EX_GeographicBoundingBox or EX_BoundingPolygon.
            # The schema also specifies an EX_GeographicDescription. This is not implemented yet.
            val = None
            val2 = None
            val3 = None
            extents = md.findall(util.nspath_eval('mri:extent', self.namespaces))
            for extent in extents:
                # Parse bounding box and vertical extents
                if val is None:
                    for e in extent.findall(util.nspath_eval('gex:EX_Extent/gex:geographicElement', self.namespaces)):
                        if e.find(util.nspath_eval('gex:EX_GeographicBoundingBox', self.namespaces)) is not None or \
                                e.find(util.nspath_eval('gex:EX_BoundingPolygon', self.namespaces)) is not None:
                            val = e
                            break
                    vert_elem = extent.find(util.nspath_eval('gex:EX_Extent/gex:verticalElement', self.namespaces))
                    self.extent = EX_Extent(self.namespaces, val, vert_elem)
                    self.bbox = self.extent.boundingBox  # for backwards compatibility

                # Parse temporal extent begin
                if val2 is None:
                    val2 = extent.find(util.nspath_eval(
                        'gex:EX_Extent/gex:temporalElement/gex:EX_TemporalExtent/gex:extent/gml:TimePeriod/gml:beginPosition',
                        self.namespaces))
                    self.temporalextent_start = util.testXMLValue(val2)

                # Parse temporal extent end
                if val3 is None:
                    val3 = extent.find(util.nspath_eval(
                        'gex:EX_Extent/gex:temporalElement/gex:EX_TemporalExtent/gex:extent/gml:TimePeriod/gml:endPosition',
                        self.namespaces))
                    self.temporalextent_end = util.testXMLValue(val3)


class MD_Distributor(printable):
    """ Process MD_Distributor
    """
    def __init__(self, namespaces, md=None):
        """
        Parses MD_Distributor XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: MD_Distributor etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.contact = None
            self.online = []
        else:
            self.contact = None
            val = md.find(util.nspath_eval(
                'mrd:MD_Distributor/mrd:distributorContact/cit:CI_Responsibility', self.namespaces))
            if val is not None:
                self.contact = CI_Responsibility(self.namespaces, val)

            self.online = []

            for ol in md.findall(util.nspath_eval(
                    'mrd:MD_Distributor/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource',
                    self.namespaces)):
                self.online.append(CI_OnlineResource(self.namespaces, ol))


class MD_Distribution(printable):
    """ Process MD_Distribution
    """
    def __init__(self, namespaces, md=None):
        """
        Parses MD_Distribution XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: MD_Distribution etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.format = None
            self.version = None
            self.distributor = []
            self.online = []
        else:
            val = md.find(util.nspath_eval(
                'mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:title/gco:CharacterString', self.namespaces))
            self.format = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:edition/gco:CharacterString', self.namespaces))
            self.version = util.testXMLValue(val)

            self.distributor = []
            for dist in md.findall(util.nspath_eval('mrd:distributor', self.namespaces)):
                self.distributor.append(MD_Distributor(self.namespaces, dist))

            self.online = []

            for ol in md.findall(util.nspath_eval(
                    'mrd:transferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource',
                    self.namespaces)):
                self.online.append(CI_OnlineResource(self.namespaces, ol))


class DQ_DataQuality(printable):
    """ Process DQ_DataQuality
    """
    def __init__(self, namespaces, md=None):
        """
        Parse a portion of DQ_DataQuality XML subtree only taking the first value found

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: DQ_DataQuality etree.Element
        """
        self.namespaces = namespaces
        self.conformancetitle = []
        self.conformancedate = []
        self.conformancedatetype = []
        self.conformancedegree = []
        self.lineage = None
        self.lineage_url = None
        self.specificationtitle = None
        self.specificationdate = []
        if md is not None:
            
            for conftitle in md.xpath(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:title/gco:CharacterString',
                    namespaces=self.namespaces):
                self.conformancetitle.append(util.testXMLValue(conftitle))

            for confdate in md.xpath(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:date/cit:CI_Date/cit:date/gco:DateTime',
                    namespaces=self.namespaces):
                self.conformancedate.append(util.testXMLValue(confdate))

            for confdatetype in md.xpath(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:date/cit:CI_Date/cit:dateType/cit:CI_DateTypeCode',
                    namespaces=self.namespaces):
                self.conformancedatetype.append(util.testXMLValue(confdatetype))

            for confdegree in md.xpath(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:pass/gco:Boolean',
                    namespaces=self.namespaces):
                self.conformancedegree.append(util.testXMLValue(confdegree))

            lins = md.xpath(
                'mdq:lineage/mrl:LI_Lineage/mrl:statement/*[self::gco:CharacterString or self::gcx:Anchor]',
                namespaces=self.namespaces)
            if len(lins) > 0:
                self.lineage = util.testXMLValue(lins[0])
                self.lineage_url = lins[0].attrib.get(util.nspath_eval('xlink:href', self.namespaces))

            val = md.find(util.nspath_eval(
                'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:title/gco:CharacterString',
                self.namespaces))
            self.specificationtitle = util.testXMLValue(val)

            self.specificationdate = []
            for i in md.findall(util.nspath_eval(
                    'mdq:report/mdq:DQ_DomainConsistency/mdq:result/mdq:DQ_ConformanceResult/mdq:specification/cit:CI_Citation/cit:date/cit:CI_Date/cit:date/gco:DateTime',
                    self.namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.specificationdate.append(val)


class SV_ServiceIdentification(MD_DataIdentification, printable):
    """ Process SV_ServiceIdentification
    """
    def __init__(self, namespaces, md=None):
        """
        Parses SV_ServiceIdentification XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: SV_ServiceIdentification etree.Element
        """
        super().__init__(namespaces, md, 'service')
        self.namespaces = namespaces

        if md is None:
            self.type = None
            self.version = None
            self.fees = None
            self.couplingtype = None
            self.operations = []
            self.operateson = []
        else:
            val = md.xpath('srv:serviceType/*[self::gco:LocalName or self::gco:ScopedName]', namespaces=self.namespaces)
            if len(val) > 0:
                self.type = util.testXMLValue(val[0])

            val = md.find(util.nspath_eval('srv:serviceTypeVersion/gco:CharacterString', self.namespaces))
            self.version = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'srv:accessProperties/mrd:MD_StandardOrderProcess/mrd:fees/gco:CharacterString', self.namespaces))
            self.fees = util.testXMLValue(val)

            self.couplingtype = _testCodeListValue(md.find(util.nspath_eval(
                'srv:couplingType/srv:SV_CouplingType', self.namespaces)))

            self.operations = []

            for i in md.findall(util.nspath_eval('srv:containsOperations', self.namespaces)):
                tmp = {}
                val = i.find(util.nspath_eval(
                    'srv:SV_OperationMetadata/srv:operationName/gco:CharacterString', self.namespaces))
                tmp['name'] = util.testXMLValue(val)
                tmp['dcplist'] = []
                for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:distributedComputingPlatform', self.namespaces)):
                    tmp2 = _testCodeListValue(d.find(util.nspath_eval('srv:DCPList', self.namespaces)))
                    tmp['dcplist'].append(tmp2)

                tmp['connectpoint'] = []

                for d in i.findall(util.nspath_eval('srv:SV_OperationMetadata/srv:connectPoint', self.namespaces)):
                    tmp3 = d.find(util.nspath_eval('cit:CI_OnlineResource', self.namespaces))
                    tmp['connectpoint'].append(CI_OnlineResource(self.namespaces, tmp3))
                self.operations.append(tmp)

            self.operateson = []

            for i in md.findall(util.nspath_eval('srv:operatesOn', self.namespaces)):
                tmp = {}
                tmp['uuidref'] = i.attrib.get('uuidref')
                tmp['href'] = i.attrib.get(util.nspath_eval('xlink:href', self.namespaces))
                tmp['title'] = i.attrib.get(util.nspath_eval('xlink:title', self.namespaces))
                self.operateson.append(tmp)


class CI_OnlineResource(printable):
    """ Process CI_OnlineResource
    """
    def __init__(self, namespaces, md=None):
        """
        Parses CI_OnlineResource XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: CI_OnlineResource etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.url = None
            self.protocol = None
            self.name = None
            self.description = None
            self.function = None
        else:
            val = md.find(util.nspath_eval('cit:linkage/gco:CharacterString', self.namespaces))
            self.url = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:protocol/gco:CharacterString', self.namespaces))
            self.protocol = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:name/gco:CharacterString', self.namespaces))
            self.name = util.testXMLValue(val)

            val = md.find(util.nspath_eval('cit:description/gco:CharacterString', self.namespaces))
            self.description = util.testXMLValue(val)

            self.function = _testCodeListValue(md.find(util.nspath_eval(
                'cit:function/cit:CI_OnLineFunctionCode', self.namespaces)))


class EX_GeographicBoundingBox(printable):
    """ Process gex:EX_GeographicBoundingBox
    """
    def __init__(self, namespaces, md=None):
        """
        Parses EX_GeographicBoundingBox XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: EX_GeographicBoundingBox etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.minx = None
            self.maxx = None
            self.miny = None
            self.maxy = None
        else:
            val = md.find(util.nspath_eval('gex:westBoundLongitude/gco:Decimal', self.namespaces))
            self.minx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:eastBoundLongitude/gco:Decimal', self.namespaces))
            self.maxx = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:southBoundLatitude/gco:Decimal', self.namespaces))
            self.miny = util.testXMLValue(val)
            val = md.find(util.nspath_eval('gex:northBoundLatitude/gco:Decimal', self.namespaces))
            self.maxy = util.testXMLValue(val)


class EX_Polygon(printable):
    """ Process gml32:Polygon
    """
    def __init__(self, namespaces, md=None):
        """
        Parses EX_Polygon XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: EX_Polygon etree.Element
        """
        self.namespaces = namespaces

        self.exterior_ring = None
        self.interior_rings = []

        if md is not None:
            try:
                linear_ring = md.find(util.nspath_eval('gml32:Polygon/gml32:exterior/gml32:LinearRing', self.namespaces))
                if linear_ring is not None:
                    self.exterior_ring = self._coordinates_for_ring(linear_ring)
            except KeyError:
                pass

            try:
                interior_ring_elements = md.findall(util.nspath_eval('gml32:Polygon/gml32:interior', self.namespaces))
                self.interior_rings = []
                if interior_ring_elements is not None:
                    for iring_element in interior_ring_elements:
                        try:
                            linear_ring = iring_element.find(util.nspath_eval('gml32:LinearRing', self.namespaces))
                            self.interior_rings.append(self._coordinates_for_ring(linear_ring))
                        except KeyError:
                            pass
            except KeyError:
                pass


    def _coordinates_for_ring(self, linear_ring):
        """ Get coordinates for gml coordinate ring

        :param linear_ring: etree.Element position list
        :returns: coordinate list of float tuples
        """
        coordinates = []
        positions = linear_ring.findall(util.nspath_eval('gml32:pos', self.namespaces))
        for pos in positions:
            tokens = pos.text.split()
            coords = tuple([float(t) for t in tokens])
            coordinates.append(coords)
        return coordinates


class EX_BoundingPolygon(printable):
    """ Process EX_BoundingPolygon
    """
    def __init__(self, namespaces, md=None):
        """
        Parses EX_BoundingPolygon XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: EX_BoundingPolygon etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.is_extent = None
            self.polygons = []
        else:
            val = md.find(util.nspath_eval('gex:extentTypeCode', self.namespaces))
            self.is_extent = util.testXMLValue(val)

            md_polygons = md.findall(util.nspath_eval('gex:polygon', self.namespaces))

            self.polygons = []
            for val in md_polygons:
                self.polygons.append(EX_Polygon(self.namespaces, val))


class EX_Extent(printable):
    """ Process EX_Extent
    """
    def __init__(self, namespaces, md=None, vert_elem=None):
        """
        Parses EX_Extent XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: EX_Extent etree.Element
        :param vert_elem: vertical extent 'gex:verticalElement' etree.Element
        """
        self.namespaces = namespaces
        self.boundingBox = None
        self.boundingPolygon = None
        self.description_code = None
        self.vertExtMin = None
        self.vertExtMax = None
        if md is not None:
            # Parse bounding box
            bboxElement = md.find(util.nspath_eval('gex:EX_GeographicBoundingBox', self.namespaces))
            if bboxElement is not None:
                self.boundingBox = EX_GeographicBoundingBox(self.namespaces, bboxElement)

            polygonElement = md.find(util.nspath_eval('gex:EX_BoundingPolygon', self.namespaces))
            if polygonElement is not None:
                self.boundingPolygon = EX_BoundingPolygon(self.namespaces, polygonElement)

            code = md.find(util.nspath_eval(
                'gex:EX_GeographicDescription/gex:geographicIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString',
                self.namespaces))
            self.description_code = util.testXMLValue(code)

        # Parse vertical extent
        if vert_elem is not None:
            # Get vertical extent max
            vertext_max = vert_elem.find(util.nspath_eval(
                'gex:EX_VerticalExtent/gex:maximumValue/gco:Real',
                self.namespaces))
            self.vertExtMax = util.testXMLValue(vertext_max)

            # Get vertical extent min
            vertext_min = vert_elem.find(util.nspath_eval(
                'gex:EX_VerticalExtent/gex:minimumValue/gco:Real',
                self.namespaces))
            self.vertExtMin = util.testXMLValue(vertext_min)


class MD_ReferenceSystem(printable):
    """ Process MD_ReferenceSystem
    """
    def __init__(self, namespaces, md=None):
        """
        Parses MD_ReferenceSystem XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param md: MD_ReferenceSystem etree.Element
        """
        self.namespaces = namespaces
        if md is None:
            self.code = None
            self.codeSpace = None
            self.version = None
        else:
            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString', self.namespaces))
            if val is not None:
                self.code = util.testXMLValue(val)
            else:
                val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gcx:Anchor', self.namespaces))
                if val is not None:
                    self.code = util.testXMLValue(val)
                else:
                    self.code = None

            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:codeSpace/gco:CharacterString', self.namespaces))
            if val is not None:
                self.codeSpace = util.testXMLValue(val)
            else:
                self.codeSpace = None

            val = md.find(util.nspath_eval(
                'mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:version/gco:CharacterString', self.namespaces))
            if val is not None:
                self.version = util.testXMLValue(val)
            else:
                self.version = None


def _testCodeListValue(elpath):
    """ Get codeListValue attribute, else get text content

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
    def __init__(self, namespaces, fcd=None):
        """
        Parses MD_FeatureCatalogueDescription XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param fcd: MD_FeatureCatalogueDescription etree.Element
        """
        self.namespaces = namespaces
        self.featuretypenames = []
        self.featurecatalogues = []
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
            comp = fcd.find(util.nspath_eval('mrc:complianceCode/gco:Boolean', self.namespaces))
            val = util.testXMLValue(comp)
            if val is not None:
                self.compliancecode = util.getTypedValue('boolean', val)

            self.language = []
            for i in fcd.findall(util.nspath_eval('mrc:locale/lan:PT_Locale/lan:language/lan:LanguageCode', self.namespaces)):
                val = _testCodeListValue(i)
                if val is not None:
                    self.language.append(val)

            self.includedwithdataset = None
            comp = fcd.find(util.nspath_eval('mrc:includedWithDataset/gco:Boolean', self.namespaces))
            val = util.testXMLValue(comp)
            if val is not None:
                self.includedwithdataset = util.getTypedValue('boolean', val)

            self.featuretypenames = []
            for name in fcd.xpath('mrc:featureTypes/mrc:MD_FeatureTypeInfo/mrc:featureTypeName/*[self::gco:LocalName or self::gco:ScopedName]',
                                   namespaces=self.namespaces):
                val = util.testXMLValue(name)
                if ValueError is not None:
                    self.featuretypenames.append(val)

            # Gather feature catalogue titles
            self.featurecatalogues = []
            for cit in fcd.findall(util.nspath_eval(
                    'mrc:featureCatalogueCitation/cit:CI_Citation/cit:title/gco:CharacterString', self.namespaces)):
                val = util.testXMLValue(cit)
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

            val = fc.find(util.nspath_eval('cat:name/gco:CharacterString', self.namespaces))
            self.name = util.testXMLValue(val)

            val = fc.find(util.nspath_eval('cat:versionDate/gco:Date', self.namespaces))
            self.versiondate = util.testXMLValue(val)

            if not self.versiondate:
                val = fc.find(util.nspath_eval('cat:versionDate/gco:DateTime', self.namespaces))
                self.versiondate = util.testXMLValue(val)

            self.producer = None
            prod = fc.find(util.nspath_eval('gfc:producer/cit:CI_Responsiblility', self.namespaces))
            if prod is not None:
                self.producer = CI_Responsibility(prod)

            self.featuretypes = []
            for i in fc.findall(util.nspath_eval('gfc:featureType/gfc:FC_FeatureType', self.namespaces)):
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

            val = ft.find(util.nspath_eval('gfc:typeName/gco:LocalName', self.namespaces))
            self.typename = util.testXMLValue(val)

            val = ft.find(util.nspath_eval('gfc:definition/gco:CharacterString', self.namespaces))
            self.definition = util.testXMLValue(val)

            self.isabstract = None
            val = ft.find(util.nspath_eval('gfc:isAbstract/gco:Boolean', self.namespaces))
            val = util.testXMLValue(val)
            if val is not None:
                self.isabstract = util.getTypedValue('boolean', val)

            self.aliases = []
            for i in ft.findall(util.nspath_eval('gfc:aliases/gco:LocalName', self.namespaces)):
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

            val = fa.find(util.nspath_eval('gfc:memberName/gco:ScopedName', self.namespaces))
            self.membername = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:definition/gco:CharacterString', self.namespaces))
            self.definition = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:code/gco:CharacterString', self.namespaces))
            self.code = util.testXMLValue(val)

            val = fa.find(util.nspath_eval('gfc:valueType/gco:TypeName/gco:aName/gco:CharacterString', self.namespaces))
            self.valuetype = util.testXMLValue(val)

            self.listedvalues = []
            for i in fa.findall(util.nspath_eval('gfc:listedValue/gfc:FC_ListedValue', self.namespaces)):
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

            val = lv.find(util.nspath_eval('gfc:label/gco:CharacterString', self.namespaces))
            self.label = util.testXMLValue(val)

            val = lv.find(util.nspath_eval('gfc:code/gco:CharacterString', self.namespaces))
            self.code = util.testXMLValue(val)

            val = lv.find(util.nspath_eval('gfc:definition/gco:CharacterString', self.namespaces))
            self.definition = util.testXMLValue(val)

class MD_ImageDescription(printable):
    """Process mrc:MD_ImageDescription
    """
    def __init__(self, namespaces, img_desc=None):
        """
        Parses MD_ImageDescription XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param img_desc: MD_ImageDescription etree.Element
        """
        self.namespaces = namespaces
        self.type = 'image'
        self.bands = []

        if img_desc is None:
            self.attributedescription = None
            self.cloudcover = None
            self.processinglevel = None
            self.illumination_elevation_angle = None
            self.illumination_azimuth_angle = None
        else:
            attdesc = img_desc.find(util.nspath_eval('mrc:attributeDescription/gco:RecordType', self.namespaces))
            self.attributedescription = util.testXMLValue(attdesc)

            ctype = img_desc.find(util.nspath_eval('mrc:attributeGroup/mrc:MD_AttributeGroup/mrc:contentType/mrc:MD_CoverageContentTypeCode', self.namespaces))
            self.type = util.testXMLAttribute(ctype, 'codeListValue')

            cloudcov = img_desc.find(util.nspath_eval('mrc:cloudCoverPercentage/gco:Real', self.namespaces))
            self.cloudcover = util.testXMLValue(cloudcov)

            iea = img_desc.find(util.nspath_eval('mrc:illuminationElevationAngle/gco:Real', self.namespaces))
            self.illumination_elevation_angle = util.testXMLValue(iea)

            iaa = img_desc.find(util.nspath_eval('mrc:illuminationAzimuthAngle/gco:Real', self.namespaces))
            self.illumination_azimuth_angle = util.testXMLValue(iaa)

            proclvl = img_desc.find(util.nspath_eval(
                'mrc:processingLevelCode/mcc:MD_Identifier/mcc:code/gco:CharacterString', self.namespaces))
            self.processinglevel = util.testXMLValue(proclvl)

            for i in img_desc.findall(util.nspath_eval('mrc:attributeGroup/mrc:MD_AttributeGroup/mrc:attribute/mrc:MD_Band', self.namespaces)):
                self.bands.append(MD_Band(self.namespaces, i))


class MD_Band(printable):
    """Process mrc:MD_Band
    """
    def __init__(self, namespaces, band):
        """
        Parses MD_Band XML subtree

        :param namespaces: dict of XML namespaces, key is namespace, val is path
        :param band: MD_Band etree.Element
        """
        self.namespaces = namespaces
        if band is None:
            self.id = None
            self.units = None
            self.min = None
            self.max = None
        else:
            seq_id = band.find(util.nspath_eval('mrc:sequenceIdentifier/gco:MemberName/gco:aName/gco:CharacterString', self.namespaces))
            self.id = util.testXMLValue(seq_id)

            units = band.find(util.nspath_eval('mrc:units/gml:UnitDefinition/gml:identifier', self.namespaces))
            self.units = util.testXMLValue(units)

            bmin = band.find(util.nspath_eval('mrc:minValue/gco:Real', self.namespaces))
            self.min = util.testXMLValue(bmin)

            bmax = band.find(util.nspath_eval('mrc:maxValue/gco:Real', self.namespaces))
            self.max = util.testXMLValue(bmax)
