# -*- coding: utf-8 -*-

import io

from owslib import util
from owslib.etree import etree
from owslib.iso import (
    MD_Metadata, Keyword, MD_Keywords
)
from owslib.namespaces import Namespaces


def get_md_resource(file_path):
    """Read the file and parse into an XML tree.

    Parameters
    ----------
    file_path : str
        Path of the file to read.

    Returns
    -------
    etree.ElementTree
        XML tree of the resource on disk.

    """
    namespaces = Namespaces().get_namespaces(keys=('gmd', 'gmi'))

    with io.open(file_path, mode='r', encoding='utf-8') as f:
        data = f.read().encode('utf-8')
        data = etree.fromstring(data)
        mdelem = data.find('.//' + util.nspath_eval(
            'gmd:MD_Metadata', namespaces))

        if mdelem is None:
            mdelem = data.find(
                './/' + util.nspath_eval('gmi:MI_Metadata', namespaces))

        if mdelem is None and data.tag in ['{http://www.isotc211.org/2005/gmd}MD_Metadata',
                                           '{http://www.isotc211.org/2005/gmi}MI_Metadata']:
            mdelem = data

    return mdelem


def assert_list(var, length):
    """Assert a given variable is a list with given size.

    Parameters
    ----------
    var : variable
        Variable to test (i.e. should be a list).
    length : int
        The length/size of the list.

    """
    assert type(var) is list
    assert len(var) == length


def test_md_parsing_dov():
    """Test the parsing of a metadatarecord from DOV

    GetRecordById response available in
    tests/resources/csw_dov_getrecordbyid.xml

    """
    md_resource = get_md_resource('tests/resources/csw_dov_getrecordbyid.xml')
    md = MD_Metadata(md_resource)

    assert type(md) is MD_Metadata

    assert md.identifier == '6c39d716-aecc-4fbc-bac8-4f05a49a78d5'
    assert md.dataseturi is None
    assert md.parentidentifier is None

    assert md.language is None
    assert md.languagecode == 'dut'

    assert md.charset == 'utf8'
    assert md.datestamp == '2018-02-21T16:14:24'

    assert md.hierarchy == 'dataset'

    assert_list(md.contact, 1)

    contact = md.contact[0]
    assert contact.organization == 'Vlaamse overheid - Vlaamse ' \
                                   'MilieuMaatschappij - Afdeling ' \
                                   'Operationeel Waterbeheer'
    assert contact.address == 'Koning Albert II-laan 20 bus 16'
    assert contact.city == 'Brussel'
    assert contact.postcode == '1000'
    assert contact.country == u'België'
    assert contact.email == 'info@vmm.be'
    assert contact.onlineresource.url == 'https://www.vmm.be'
    assert contact.role == 'pointOfContact'

    assert md.stdname == 'ISO 19115/2003/Cor.1:2006'
    assert md.stdver == 'GDI-Vlaanderen Best Practices - versie 1.0'

    assert md.referencesystem.code == '31370'
    assert md.referencesystem.codeSpace == 'EPSG'

    assert_list(md.identification, 1)

    iden = md.identification[0]
    assert iden.title == 'Grondwatermeetnetten'
    assert iden.alternatetitle == 'Grondwatermeetnetten beschikbaar op DOV'

    assert_list(iden.date, 2)
    assert iden.date[0].date == '2002-05-22'
    assert iden.date[0].type == 'creation'
    assert iden.date[1].date == '2002-05-22'
    assert iden.date[1].type == 'publication'

    assert_list(iden.uricode, 1)
    assert iden.uricode[0] == 'A64F073B-9FBE-91DD-36FDE7462BBAFA61'

    assert_list(iden.uricodespace, 1)
    assert iden.uricodespace[0] == 'DOV-be'

    assert_list(iden.uselimitation, 3)
    assert "Zie 'Overige beperkingen'" in iden.uselimitation
    assert "Bij het gebruik van de informatie die DOV aanbiedt, dient steeds " \
           "volgende standaardreferentie gebruikt te worden: Databank " \
           "Ondergrond Vlaanderen - (vermelding van de beheerder en de " \
           "specifieke geraadpleegde gegevens) - Geraadpleegd op dd/mm/jjjj, " \
           "op https://www.dov.vlaanderen.be" in iden.uselimitation
    assert "Volgende aansprakelijkheidsbepalingen gelden: " \
           "https://www.dov.vlaanderen.be/page/disclaimer" in iden.uselimitation

    assert_list(iden.uselimitation_url, 0)

    assert_list(iden.accessconstraints, 1)
    assert iden.accessconstraints[0] == 'otherRestrictions'

    assert_list(iden.classification, 0)

    assert_list(iden.otherconstraints, 2)
    assert iden.otherconstraints_url[
               1] == "https://inspire.ec.europa.eu/metadata-codelist/ConditionsApplyingToAccessAndUse/noConditionsApply"
    assert iden.otherconstraints[
               0] == "Data beschikbaar voor hergebruik volgens de " \
                     "Modellicentie Gratis Hergebruik. Toelichting " \
                     "beschikbaar op " \
                     "https://www.dov.vlaanderen.be/page/gebruiksvoorwaarden-dov-services"

    assert_list(iden.securityconstraints, 1)
    assert iden.securityconstraints[0] == 'unclassified'

    assert_list(iden.useconstraints, 0)

    assert_list(iden.denominators, 1)
    assert iden.denominators[0] == '10000'

    assert_list(iden.distance, 0)
    assert_list(iden.uom, 0)

    assert_list(iden.resourcelanguage, 0)
    assert_list(iden.resourcelanguagecode, 1)
    assert iden.resourcelanguagecode[0] == 'dut'

    assert_list(iden.creator, 0)
    assert_list(iden.publisher, 0)
    assert_list(iden.contributor, 0)

    assert iden.edition is None

    assert iden.abstract.startswith("In de Databank Ondergrond Vlaanderen "
                                    "zijn verschillende grondwatermeetnetten "
                                    "opgenomen.")

    assert iden.purpose.startswith(
        "Het doel van de meetnetten is inzicht krijgen in de kwaliteit en "
        "kwantiteit van de watervoerende lagen in de ondergrond van "
        "Vlaanderen. Algemeen kan gesteld worden dat de grondwatermeetnetten "
        "een belangrijk beleidsinstrument vormen")

    assert iden.status == 'onGoing'

    assert_list(iden.contact, 2)

    assert iden.contact[0].organization == 'Vlaamse overheid - Vlaamse MilieuMaatschappij - Afdeling Operationeel Waterbeheer'
    assert iden.contact[0].address == 'Koning Albert II-laan 20 bus 16'
    assert iden.contact[0].city == 'Brussel'
    assert iden.contact[0].postcode == '1000'
    assert iden.contact[0].country == u'België'
    assert iden.contact[0].email == 'info@vmm.be'
    assert iden.contact[0].onlineresource.url == 'https://www.vmm.be'
    assert iden.contact[0].role == 'pointOfContact'

    assert iden.contact[1].organization == 'Databank Ondergrond Vlaanderen (' \
                                           'DOV)'
    assert iden.contact[1].address == 'Technologiepark Gebouw 905'
    assert iden.contact[1].city == 'Zwijnaarde'
    assert iden.contact[1].postcode == '9052'
    assert iden.contact[1].country == u'België'
    assert iden.contact[1].email == 'dov@vlaanderen.be'
    assert iden.contact[1].onlineresource.url == \
           'https://www.dov.vlaanderen.be'
    assert iden.contact[1].role == 'distributor'

    assert_list(iden.spatialrepresentationtype, 1)
    assert iden.spatialrepresentationtype[0] == 'vector'

    assert_list(iden.keywords, 5)

    assert type(iden.keywords[0]) is MD_Keywords
    assert iden.keywords[0].type == ''
    assert iden.keywords[0].thesaurus['title'] == "GEMET - INSPIRE thema's, versie 1.0"
    assert iden.keywords[0].thesaurus['date'] == '2008-06-01'
    assert iden.keywords[0].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[0].keywords, 1)
    assert iden.keywords[0].keywords[0].name == 'Geologie'

    assert type(iden.keywords[1]) is MD_Keywords
    assert iden.keywords[1].type == ''
    assert iden.keywords[1].thesaurus[
               'title'] == "GEMET - Concepten, versie 2.4"
    assert iden.keywords[1].thesaurus['date'] == '2010-01-13'
    assert iden.keywords[1].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[1].keywords, 2)
    assert iden.keywords[1].keywords[0].name == 'grondwater'
    assert iden.keywords[1].keywords[1].name == 'meetnet(werk)'

    assert type(iden.keywords[2]) is MD_Keywords
    assert iden.keywords[2].type == ''
    assert iden.keywords[2].thesaurus[
               'title'] == "Vlaamse regio's"
    assert iden.keywords[2].thesaurus['date'] == '2013-09-25'
    assert iden.keywords[2].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[2].keywords, 1)
    assert iden.keywords[2].keywords[0].name == 'Vlaams Gewest'

    assert type(iden.keywords[3]) is MD_Keywords
    assert iden.keywords[3].type is None
    assert iden.keywords[3].thesaurus[
               'title'] == "GDI-Vlaanderen Trefwoorden"
    assert iden.keywords[3].thesaurus['date'] == '2014-02-26'
    assert iden.keywords[3].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[3].keywords, 7)
    assert [kw.name for kw in iden.keywords[3].keywords] == [
        'Toegevoegd GDI-Vl', 'Herbruikbaar', 'Vlaamse Open data',
        'Kosteloos', 'Lijst M&R INSPIRE', 'Metadata INSPIRE-conform',
        'Metadata GDI-Vl-conform']

    assert type(iden.keywords[4]) is MD_Keywords
    assert iden.keywords[4].type is None
    assert iden.keywords[4].thesaurus['title'] == "DOV"
    assert iden.keywords[4].thesaurus['date'] == '2010-12-01'
    assert iden.keywords[4].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[4].keywords, 7)
    assert [kw.name for kw in iden.keywords[4].keywords] == [
        'Ondergrond', 'DOV', 'Vlaanderen', 'monitoring', 'meetnetten',
        'Kaderrichtlijn Water', 'Decreet Integraal waterbeleid']

    assert_list(iden.keywords, 5)
    assert iden.keywords[0].type == ''
    assert iden.keywords[0].thesaurus[
               'title'] == "GEMET - INSPIRE thema's, versie 1.0"
    assert iden.keywords[0].thesaurus['date'] == '2008-06-01'
    assert iden.keywords[0].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[0].keywords, 1)
    assert iden.keywords[0].keywords[0].name == 'Geologie'

    assert iden.keywords[1].type == ''
    assert iden.keywords[1].thesaurus[
               'title'] == "GEMET - Concepten, versie 2.4"
    assert iden.keywords[1].thesaurus['date'] == '2010-01-13'
    assert iden.keywords[1].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[1].keywords, 2)
    assert [kw.name for kw in iden.keywords[1].keywords] == ['grondwater', 'meetnet(werk)']

    assert iden.keywords[2].type == ''
    assert iden.keywords[2].thesaurus[
               'title'] == "Vlaamse regio's"
    assert iden.keywords[2].thesaurus['date'] == '2013-09-25'
    assert iden.keywords[2].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[2].keywords, 1)
    assert iden.keywords[2].keywords[0].name == 'Vlaams Gewest'

    assert iden.keywords[3].type is None
    assert iden.keywords[3].thesaurus[
               'title'] == "GDI-Vlaanderen Trefwoorden"
    assert iden.keywords[3].thesaurus['date'] == '2014-02-26'
    assert iden.keywords[3].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[3].keywords, 7)
    assert [kw.name for kw in iden.keywords[3].keywords] == [
        'Toegevoegd GDI-Vl', 'Herbruikbaar', 'Vlaamse Open data',
        'Kosteloos', 'Lijst M&R INSPIRE', 'Metadata INSPIRE-conform',
        'Metadata GDI-Vl-conform']

    assert iden.keywords[4].type is None
    assert iden.keywords[4].thesaurus['title'] == "DOV"
    assert iden.keywords[4].thesaurus['date'] == '2010-12-01'
    assert iden.keywords[4].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[4].keywords, 7)
    assert [kw.name for kw in iden.keywords[4].keywords] == [
        'Ondergrond', 'DOV', 'Vlaanderen', 'monitoring', 'meetnetten',
        'Kaderrichtlijn Water', 'Decreet Integraal waterbeleid']

    assert_list(iden.topiccategory, 1)
    assert iden.topiccategory[0] == 'geoscientificInformation'

    assert iden.supplementalinformation == \
           "https://www.dov.vlaanderen.be/page/grondwatermeetnet"

    assert_list(md.contentinfo, 1)
    ci = md.contentinfo[0]

    assert ci.compliancecode is None
    assert_list(ci.language, 0)
    assert ci.includedwithdataset == True
    assert_list(ci.featuretypenames, 0)

    assert_list(ci.featurecatalogues, 1)
    assert ci.featurecatalogues[0] == 'b142965f-b2aa-429e-86ff-a7cb0e065d48'


def test_md_parsing_geobretagne():
    """Test the parsing of a metadatarecord from GéoBretagne

    MD_Metadata record available in
    tests/resources/csw_geobretagne_mdmetadata.xml

    """
    md_resource = get_md_resource(
        'tests/resources/csw_geobretagne_mdmetadata.xml')
    md = MD_Metadata(md_resource)

    assert type(md) is MD_Metadata

    assert md.identifier == '955c3e47-411e-4969-b61b-3556d1b9f879'
    assert md.dataseturi is None
    assert md.parentidentifier is None

    assert md.language == 'fre'
    assert md.languagecode is None

    assert md.charset == 'utf8'
    assert md.datestamp == '2018-07-30T14:19:40'

    assert md.hierarchy == 'dataset'

    assert_list(md.contact, 1)

    contact = md.contact[0]
    assert contact.organization == 'DIRECTION GENERALE DES FINANCES ' \
                                   'PUBLIQUES BUREAU GF-3A'
    assert contact.address is None
    assert contact.city is None
    assert contact.postcode is None
    assert contact.country is None
    assert contact.email == 'bureau.gf3a@dgfip.finances.gouv.fr'
    assert contact.onlineresource is None
    assert contact.role == 'pointOfContact'

    assert md.stdname == 'ISO 19115'
    assert md.stdver == '1.0'

    assert md.referencesystem.code == 'RGF93 / CC48 (EPSG:3948)'
    assert md.referencesystem.codeSpace == 'EPSG'

    assert_list(md.identification, 1)

    iden = md.identification[0]
    assert iden.title == 'Cadastre 2018 en Bretagne'
    assert iden.alternatetitle is None

    assert_list(iden.date, 1)
    assert iden.date[0].date == '2018-09-01'
    assert iden.date[0].type == 'revision'

    assert_list(iden.uricode, 1)
    assert iden.uricode[0] == 'https://geobretagne.fr/geonetwork/apps/georchestra/?uuid=363e3a8e-d0ce-497d-87a9-2a2d58d82772'
    assert_list(iden.uricodespace, 0)

    assert_list(iden.uselimitation, 2)
    assert u"le plan cadastral décrit les limites apparentes de la " \
           u"propriété." in iden.uselimitation

    assert_list(iden.uselimitation_url, 0)

    assert_list(iden.accessconstraints, 1)
    assert iden.accessconstraints[0] == 'otherRestrictions'

    assert_list(iden.classification, 0)

    assert_list(iden.otherconstraints, 1)
    assert iden.otherconstraints[
               0] == u'Usage libre sous réserve des mentions obligatoires ' \
                     u'sur tout document de diffusion : "Source : DGFIP"'

    assert_list(iden.securityconstraints, 0)

    assert_list(iden.useconstraints, 1)
    assert iden.useconstraints[0] == 'copyright'

    assert_list(iden.denominators, 1)
    assert iden.denominators[0] == '500'

    assert_list(iden.distance, 0)
    assert_list(iden.uom, 0)

    assert_list(iden.resourcelanguage, 1)
    assert iden.resourcelanguage[0] == 'fre'
    assert_list(iden.resourcelanguagecode, 0)

    assert_list(iden.creator, 0)
    assert_list(iden.publisher, 0)
    assert_list(iden.contributor, 0)

    assert iden.edition is None

    assert iden.abstract.startswith(
        u"Le plan du cadastre est un document administratif qui propose "
        u"l’unique plan parcellaire à grande échelle couvrant le territoire "
        u"national.")

    assert iden.purpose.startswith(
        u"Le but premier du plan cadastral est d'identifier, de localiser et "
        u"représenter la propriété foncière, ainsi que de servir à l'assise "
        u"de la fiscalité locale des propriétés non bâties.")

    assert iden.status == 'completed'

    assert_list(iden.contact, 1)

    assert iden.contact[0].organization == 'DGFIP Bretagne'
    assert iden.contact[0].name == 'DIRECTION GENERALE DES FINANCES PUBLIQUES'
    assert iden.contact[0].address is None
    assert iden.contact[0].city is None
    assert iden.contact[0].postcode is None
    assert iden.contact[0].country is None
    assert iden.contact[0].email == 'bureau.gf3a@dgfip.finances.gouv.fr'
    assert iden.contact[0].onlineresource is None
    assert iden.contact[0].role == 'pointOfContact'

    assert_list(iden.spatialrepresentationtype, 1)
    assert iden.spatialrepresentationtype[0] == 'vector'

    assert_list(iden.keywords, 6)

    assert type(iden.keywords[0]) is MD_Keywords
    assert iden.keywords[0].type == 'place'
    assert iden.keywords[0].thesaurus is None
    assert_list(iden.keywords[0].keywords, 1)
    assert iden.keywords[0].keywords[0].name == 'France'

    assert type(iden.keywords[1]) is MD_Keywords
    assert iden.keywords[1].type == 'theme'
    assert iden.keywords[1].thesaurus is None
    assert_list(iden.keywords[1].keywords, 7)

    assert type(iden.keywords[2]) is MD_Keywords
    assert iden.keywords[2].type == 'theme'
    assert iden.keywords[2].thesaurus is None
    assert_list(iden.keywords[2].keywords, 5)
    assert [kw.name for kw in iden.keywords[2].keywords] == [
        'bâtis', 'sections', 'parcelles', 'cadastre', 'cadastrale']

    assert type(iden.keywords[3]) is MD_Keywords
    assert iden.keywords[3].type == 'theme'
    assert iden.keywords[3].thesaurus is not None
    assert iden.keywords[3].thesaurus['date'] == '2014-01-13'
    assert iden.keywords[3].thesaurus['datetype'] == 'publication'
    assert iden.keywords[3].thesaurus['title'] == 'GéoBretagne v 2.0'
    assert iden.keywords[3].thesaurus['url'] is None
    assert_list(iden.keywords[3].keywords, 1)
    assert [kw.name for kw in iden.keywords[3].keywords] == ['référentiels : cadastre']

    assert type(iden.keywords[4]) is MD_Keywords
    assert iden.keywords[4].type == 'theme'
    assert iden.keywords[4].thesaurus['title'] == 'INSPIRE themes'
    assert iden.keywords[4].thesaurus['date'] == '2008-06-01'
    assert iden.keywords[4].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[4].keywords, 1)
    assert [kw.name for kw in iden.keywords[4].keywords] == ['Parcelles cadastrales']

    assert type(iden.keywords[5]) is MD_Keywords
    assert iden.keywords[5].type == 'theme'
    assert iden.keywords[5].thesaurus['title'] == "GEMET"
    assert iden.keywords[5].thesaurus['date'] == '2012-07-20'
    assert iden.keywords[5].thesaurus['datetype'] == 'publication'
    assert_list(iden.keywords[5].keywords, 2)
    assert [kw.name for kw in iden.keywords[5].keywords] == ['cadastre', u'bâtiment']

    assert_list(iden.keywords, 6)

    assert_list(iden.topiccategory, 1)
    assert iden.topiccategory[0] == 'planningCadastre'

    assert iden.supplementalinformation == \
           u"La légende du plan cadastral est consultable sur: " \
           "http://www.cadastre.gouv.fr/scpc/pdf/legendes/FR_fr/Legende%20du" \
           "%20plan%20sur%20internet.pdf"

    assert_list(md.contentinfo, 1)
    ci = md.contentinfo[0]

    assert ci.compliancecode is None
    assert_list(ci.language, 0)
    assert ci.includedwithdataset == False
    assert_list(ci.featuretypenames, 0)
    assert_list(ci.featurecatalogues, 0)


def test_md_parsing_19115_2():
    """Test the parsing of a 19115-2 document

    MD_Metadata record available in
    tests/resources/iso_mi.xml

    """
    md_resource = get_md_resource(
        'tests/resources/iso_mi.xml')
    md = MD_Metadata(md_resource)

    assert type(md) is MD_Metadata

    assert md.identifier == '3f342f64-9348-11df-ba6a-0014c2c00eab'

    iden = md.identification[0]

    assert len(iden.keywords) == 3
    assert iden.keywords[1].thesaurus['title'] == 'My Vocabulary'
    assert iden.keywords[1].thesaurus['url'] == 'https://example.org/my-vocab'

    ci = md.contentinfo[0]
    assert ci.type == 'image'
    assert ci.cloud_cover == '72'
    assert ci.processing_level == '1.0'

    band = ci.bands[0]
    assert band.id == 'B1'
    assert band.units == 'nm'
    assert band.min == '932'
    assert band.max == '958'

    plt = md.acquisition.platforms[0]
    assert plt.identifier == 'LANDSAT_8'
    assert plt.description == 'Landsat 8'

    inst = plt.instruments[0]
    assert inst.identifier == 'OLI_TIRS'
    assert inst.type == 'INS-NOBS'

def test_md_parsing_keywords_anchor():
    """Test the parsing of MD_Keywords where the keyword is defined by a 
    gmx:Anchor
    
    MD_Metadata record available in
    tests/resources/iso_keywords_anchor.xml
    
    """
    md_resource = get_md_resource(
        'tests/resources/iso_keywords_anchor.xml')
    md = MD_Metadata(md_resource)
    
    assert type(md) is MD_Metadata
    assert md.identifier == 'ie.marine.data:dataset.1135'
    
    iden = md.identification[0]
    assert len(iden.keywords) == 1
    assert len(iden.keywords[0].keywords) == 6
    assert type(iden.keywords[0].keywords[0]) is Keyword
    assert iden.keywords[0].keywords[0].name == 'Atmospheric pressure'
    assert iden.keywords[0].keywords[0].url == 'http://vocab.nerc.ac.uk/collection/A05/current/EV_AIRPRESS/'
    assert iden.keywords[0].thesaurus['title'] == 'AtlantOS Essential Variables'
    assert iden.keywords[0].thesaurus['url'] == 'http://vocab.nerc.ac.uk/collection/A05/current/'
    
def test_md_parsing_keywords_no_anchor():
    """Test the parsing of MD_Keywords where the keyword is not defined by a 
    gmx:Anchor
    
    MD_Metadata record available in
    tests/resources/csw_geobretagne_mdmetadata.xml

    """
    md_resource = get_md_resource(
        'tests/resources/csw_geobretagne_mdmetadata.xml')
    md = MD_Metadata(md_resource)
    assert type(md) is MD_Metadata
    
    iden = md.identification[0]
    assert len(iden.keywords) == 6
    assert len(iden.keywords[0].keywords) == 1
    assert type(iden.keywords[0].keywords[0]) is Keyword
    assert iden.keywords[0].keywords[0].name == 'France'
    assert iden.keywords[0].keywords[0].url is None
    
    assert len(iden.keywords[1].keywords) == 7
    assert iden.keywords[1].keywords[0].name == 'bâtiments'
    assert iden.keywords[1].keywords[0].url is None
    assert iden.keywords[1].keywords[1].name == 'adresses'
    assert iden.keywords[1].keywords[1].url is None
    assert iden.keywords[1].keywords[2].name == 'parcelles cadastrales'
    assert iden.keywords[1].keywords[2].url is None

def test_md_indentifier_anchor():
    """Test the parsing of identifier where the id is defined by a 
    gmx:Anchor
    
    MD_Metadata record available in
    tests/resources/csw_iso_identifier.xml

    """
    md_resource = get_md_resource(
        'tests/resources/csw_iso_identifier.xml')
    md = MD_Metadata(md_resource)
    assert type(md) is MD_Metadata
    assert md.referencesystem.code == 'ETRS89-GRS80'
    assert md.referencesystem.code_url == 'http://www.opengis.net/def/crs/EPSG/0/4937'
    
    iden = md.identification[0]
    assert_list(iden.uricode, 1)
    assert iden.uricode[0] == 'https://www.nationaalgeoregister.nl/geonetwork/srv/metadata/f44dac86-2228-412f-8355-e56446ca9933'
    assert iden.contact[0].organization_url == 'http://standaarden.overheid.nl/owms/terms/Ministerie_van_Defensie'
    assert iden.keywords[0].keywords[0].url == 'http://www.eionet.europa.eu/gemet/nl/inspire-theme/am'
    assert_list(iden.otherconstraints, 3)
    assert_list(iden.otherconstraints_url, 3)
    assert iden.otherconstraints[0] == 'Geen beperkingen'
    assert iden.otherconstraints_url[0] == 'http://creativecommons.org/publicdomain/mark/1.0/deed.nl' 
    assert iden.otherconstraints[2] == 'Geen beperkingen voor publieke toegang'
    assert iden.otherconstraints_url[2] == 'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations'
    
    dist = md.distribution
    assert dist.format_url == 'http://www.iana.org/assignments/media-types/application/gml+xml'
    assert dist.format == 'gml+xml'
    assert dist.version == 'GML, version 3.2.1'
    assert dist.specification_url == 'http://inspire.ec.europa.eu/id/document/tg/hy'
    assert dist.specification == 'Data specificatie hydrografie'
    
    assert dist.online[0].protocol == 'OGC:WMS'
    assert dist.online[0].protocol_url == 'http://www.opengis.net/def/serviceType/ogc/wms'
    assert dist.online[0].applicationprofile == 'view'
    assert dist.online[0].applicationprofile_url == 'http://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceType/view'

    assert dist.online[2].protocol == 'INSPIRE Atom'
    assert dist.online[2].protocol_url == 'https://tools.ietf.org/html/rfc4287'
    assert dist.online[2].applicationprofile == 'download'
    assert dist.online[2].applicationprofile_url == 'http://inspire.ec.europa.eu/metadata-codelist/SpatialDataServiceType/download'

    assert md.dataquality.lineage == 'Ministerie van Defensie, Koninklijke Marine, Dienst der Hydrografie'
    assert md.dataquality.conformancetitle[0] == 'VERORDENING (EU) Nr. 1089/2010 VAN DE COMMISSIE van 23 november 2010 ter uitvoering van Richtlijn 2007/2/EG van het Europees Parlement en de Raad betreffende de interoperabiliteit van verzamelingen ruimtelijke gegevens en van diensten met betrekking tot ruimtelijke gegevens'
    assert md.dataquality.conformancedegree[0] == 'true'
