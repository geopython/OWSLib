# =================================================================
#
# Author: Vincent Fazio <vincent.fazio@csiro.au>
#
# Copyright (c) 2023 CSIRO Australia
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
""" Unit tests for owslib.iso3
This tests its ability to parse ISO19115-3 XML

"""

from pathlib import Path
import pytest

from owslib.etree import etree

from owslib.iso3 import (MD_Metadata, SV_ServiceIdentification, PT_Locale,
                          CI_Date, CI_Responsibility, Keyword, MD_Keywords,
                          MD_DataIdentification, MD_Distributor, MD_Distribution,
                          DQ_DataQuality, SV_ServiceIdentification, 
                          CI_OnlineResource, EX_GeographicBoundingBox,
                          EX_Polygon, EX_BoundingPolygon, EX_Extent,
                          MD_ReferenceSystem, MD_FeatureCatalogueDescription,
                          MD_ImageDescription, MD_Band)


@pytest.fixture
def ns():
    """ Create a V2 namespace
    """
    md =  MD_Metadata()
    return md.namespaces

def test_md_metadata_empty():
    """ Test empty MD_Metadata
    """
    mdb = MD_Metadata()
    assert mdb.md == None
    assert mdb.xml == None
    assert mdb.identifier == None
    assert mdb.parentidentifier == None
    assert mdb.language == None
    assert mdb.dataseturi == None
    assert mdb.languagecode == None
    assert mdb.datestamp == None
    assert mdb.charset == None
    assert mdb.hierarchy == None
    assert mdb.contact == []
    assert mdb.datetimestamp == None
    assert mdb.stdname == None
    assert mdb.stdver == None
    assert mdb.locales == []
    assert mdb.referencesystem == None
    assert mdb.identification == []
    assert mdb.contentinfo == []
    assert mdb.distribution == None
    assert mdb.dataquality == None
    assert mdb.acquisition == None

def test_pt_locale_empty(ns):
    """ Test empty PT_Locale
    """
    loc = PT_Locale(ns)
    assert loc.id == None
    assert loc.languagecode == None
    assert loc.charset == None

def test_ci_date_empty(ns):
    """ Test empty CI_Date
    """
    dat = CI_Date(ns)
    assert dat.date == None
    assert dat.type == None

def test_ci_responsibility_empty(ns):
    """ Test empty 
    """
    resp = CI_Responsibility(ns)
    assert resp.name == None
    assert resp.organization == None
    assert resp.position == None
    assert resp.phone == None
    assert resp.fax == None
    assert resp.address == None
    assert resp.city == None
    assert resp.region == None
    assert resp.postcode == None
    assert resp.country == None
    assert resp.email == None
    assert resp.onlineresource == None
    assert resp.role == None

def test_keyword_empty(ns):
    """ Test empty Keyword
    """
    keyw = Keyword(ns)
    assert keyw.name == None
    assert keyw.url == None

def test_md_keywords_empty(ns):
    """ Test empty MD_Keywords
    """
    mdk = MD_Keywords(ns)
    assert mdk.keywords == []
    assert mdk.type == None
    assert mdk.thesaurus == None
    assert mdk.kwdtype_codeList == 'http://standards.iso.org/iso/19115/-3/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode'

def test_md_dataidentification_empty(ns):
    """ Test empty MD_DataIdentification
    """
    mdi = MD_DataIdentification(ns)
    mdi.identtype == None
    assert mdi.title == None
    assert mdi.alternatetitle == None
    assert mdi.uricode == []
    assert mdi.uricodespace == []
    assert mdi.date == []
    assert mdi.datetype == []
    assert mdi.uselimitation == []
    assert mdi.uselimitation_url == []
    assert mdi.accessconstraints == []
    assert mdi.classification == []  # Left empty - no legal classification equivalent
    assert mdi.otherconstraints == []
    assert mdi.securityconstraints == []
    assert mdi.useconstraints == []
    assert mdi.denominators == []
    assert mdi.distance == []
    assert mdi.uom == []
    assert mdi.resourcelanguage == []
    assert mdi.resourcelanguagecode == []
    assert mdi.creator == []
    assert mdi.publisher == []
    assert mdi.funder == []
    assert mdi.contributor == []
    assert mdi.edition == None
    assert mdi.abstract == None
    assert mdi.abstract_url == None
    assert mdi.purpose == None
    assert mdi.status == None
    assert mdi.graphicoverview == []
    assert mdi.contact == []
    assert mdi.keywords == []
    assert mdi.topiccategory == []
    assert mdi.supplementalinformation == None
    assert mdi.extent == None
    assert mdi.bbox == None
    assert mdi.temporalextent_start == None
    assert mdi.temporalextent_end == None
    assert mdi.spatialrepresentationtype == []

def test_md_distributor_empty(ns):
    """ Test empty MD_Distributor
    """
    mdd = MD_Distributor(ns)
    assert mdd.contact == None
    assert mdd.online == []

def test_md_distribution_empty(ns):
    """ Test empty MD_Distribution
    """
    mdd = MD_Distribution(ns)
    assert mdd.format == None
    assert mdd.version == None
    assert mdd.distributor == []
    assert mdd.online == []

def test_dq_dataquality_empty(ns):
    """ Test empty DQ_DataQuality
    """
    dqd = DQ_DataQuality(ns)
    assert dqd.conformancetitle == []
    assert dqd.conformancedate == []
    assert dqd.conformancedatetype == []
    assert dqd.conformancedegree == []
    assert dqd.lineage == None
    assert dqd.lineage_url == None
    assert dqd.specificationtitle == None
    assert dqd.specificationdate == []

def test_sv_serviceidentification_empty(ns):
    """ Test empty SV_ServiceIdentification
    """
    svs = SV_ServiceIdentification(ns)
    assert svs.type == None
    assert svs.version == None
    assert svs.fees == None
    assert svs.couplingtype == None
    assert svs.operations == []
    assert svs.operateson == []

def test_ci_onlineresource_empty(ns):
    """ Test empty CI_OnlineResource
    """
    cio = CI_OnlineResource(ns)
    assert cio.url == None
    assert cio.protocol == None
    assert cio.name == None
    assert cio.description == None
    assert cio.function == None

def test_ex_geographicboundingbox_empty(ns):
    """ Test empty EX_GeographicBoundingBox
    """
    exg = EX_GeographicBoundingBox(ns)
    assert exg.minx == None
    assert exg.maxx == None
    assert exg.miny == None
    assert exg.maxy == None

def test_ex_polygon_empty(ns):
    """ Test empty EX_Polygon
    """
    exp = EX_Polygon(ns)
    assert exp.exterior_ring == None
    assert exp.interior_rings == []

def test_ex_boundingpolygon_empty(ns):
    """ Test empty EX_BoundingPolygon
    """
    exb = EX_BoundingPolygon(ns)
    assert exb.is_extent == None
    assert exb.polygons == []

def test_ex_extent_empty(ns):
    """ Test empty EX_Extent
    """
    exe = EX_Extent(ns)
    assert exe.boundingBox == None
    assert exe.boundingPolygon == None
    assert exe.description_code == None
    assert exe.vertExtMin == None
    assert exe.vertExtMax == None

def test_md_referencesystem_empty(ns):
    """ Test empty MD_ReferenceSystem
    """
    mdr = MD_ReferenceSystem(ns)
    assert mdr.code == None
    assert mdr.codeSpace == None
    assert mdr.version == None

def test_md_featurecataloguedescription_empty(ns):
    """ Test empty MD_FeatureCatalogueDescription
    """
    mdf = MD_FeatureCatalogueDescription(ns)
    assert mdf.xml == None
    assert mdf.compliancecode == None
    assert mdf.language == []
    assert mdf.includedwithdataset == None
    assert mdf.featuretypenames == []
    assert mdf.featurecatalogues == []

def test_md_imagedescription_empty(ns):
    """ Test empty MD_ImageDescription
    """
    mdi = MD_ImageDescription(ns)
    assert mdi.type == 'image'
    assert mdi.bands == []
    assert mdi.attributedescription == None
    assert mdi.cloudcover == None
    assert mdi.processinglevel == None

def test_md_band_empty(ns):
    """ Test empty MD_Band
    """
    mdb = MD_Band(ns, None)
    assert mdb.id == None
    assert mdb.units == None
    assert mdb.min == None
    assert  mdb.max == None


@pytest.fixture
def bmd():
    """ Create an MD_Metadata instance from Belgian ISO 19115 Part 3 XML sample
    
    Source: https://metawal.wallonie.be/geonetwork
    """
    belgian_sample = str(Path(__file__).parent.parent / "tests" / "resources" / "iso3_examples" / "metawal.wallonie.be-catchments.xml")
    with open(belgian_sample, "r", encoding="utf-8") as f_d:
        xml_list = f_d.readlines()
        xml_str = ''.join(xml_list)
        xml_bytes = bytes(xml_str, encoding='utf-8')
        exml = etree.fromstring(xml_bytes)
        assert exml is not None
        return MD_Metadata(exml)

def test_metadata(bmd):
    """ Tests MD_Metadata class
    """
    assert bmd is not None
    assert bmd.charset == 'utf8'
    assert bmd.hierarchy == 'series'
    assert bmd.identifier == '74f81503-8d39-4ec8-a49a-c76e0cd74946'
    assert bmd.languagecode == 'fre'
    assert bmd.locales[0].charset == 'utf8'
    assert bmd.locales[0].id == 'FR'
    assert bmd.locales[0].languagecode == 'fre'
    assert bmd.referencesystem.code == 'EPSG:31370'
    assert bmd.stdname == 'ISO 19115'
    assert bmd.stdver == '2003/Cor 1:2006'
    assert bytes(bmd.contentinfo[0].featurecatalogues[0], 'utf-8') == b'Mod\xc3\xa8le de donn\xc3\xa9es'
    assert bmd.dataseturi == 'PROTECT_CAPT'
    assert bmd.datestamp == '2023-08-08T07:34:11.366Z'
    assert bmd.datestamp == '2023-08-08T07:34:11.366Z'

def test_responsibility(bmd):
    """ Tests CI_Responsibility class as 'pointOfContact'
    """
    ct0 = bmd.contact[0]
    assert ct0.email == 'veronique.willame@spw.wallonie.be'
    assert bytes(ct0.name, 'utf-8') == b'V\xc3\xa9ronique Willame'
    assert bytes(ct0.organization, 'utf-8') == b"Direction des Eaux souterraines (SPW - Agriculture, Ressources naturelles et Environnement - D\xc3\xa9partement de l'Environnement et de l'Eau - Direction des Eaux souterraines)"
    assert ct0.phone == '+32 (0)81/335923'
    assert ct0.role == 'pointOfContact'

def test_distributor(bmd):
    """ Tests MD_Distributor class
    """
    distor = bmd.distribution.distributor[0]
    assert distor.contact.email == 'helpdesk.carto@spw.wallonie.be'
    assert distor.contact.organization == 'Service public de Wallonie (SPW)'
    assert distor.contact.role == 'distributor'

def test_online_distribution(bmd):
    """ Tests MD_Distribution class
    """
    online = bmd.distribution.online[0]
    assert online.description[:65] == 'Application cartographique du Geoportail (WalOnMap) qui permet de'
    assert online.function == 'information'
    assert bytes(online.name, 'utf=8') == b'Application WalOnMap - Toute la Wallonie \xc3\xa0 la carte'
    assert online.protocol == 'WWW:LINK'
    assert online.url == 'https://geoportail.wallonie.be/walonmap/#ADU=https://geoservices.wallonie.be/arcgis/rest/services/EAU/PROTECT_CAPT/MapServer'
    assert len(bmd.distribution.online) == 5
    assert bmd.distribution.version == '-'

def test_identification(bmd):
    """ Tests MD_DataIdentification class
    """
    ident = bmd.identification[0]
    assert bytes(ident.abstract[:62], 'utf-8') == b'Cette collection de donn\xc3\xa9es comprend les zones de surveillance'
    assert ident.accessconstraints[0] == 'license'
    assert ident.uselimitation == []
    assert ident.resourcelanguage == []
    assert ident.resourcelanguagecode[0] == 'fre'
    assert ident.alternatetitle == 'PROTECT_CAPT'
    assert ident.graphicoverview[0] == 'https://metawal.wallonie.be/geonetwork/srv/api/records/74f81503-8d39-4ec8-a49a-c76e0cd74946/attachments/PROTECT_CAPT.png'
    assert ident.graphicoverview[1] == 'https://metawal.wallonie.be/geonetwork/srv/api/records/74f81503-8d39-4ec8-a49a-c76e0cd74946/attachments/PROTECT_CAPT_s.png'
    assert ident.identtype =='dataset'
    assert bytes(ident.otherconstraints[0], 'utf-8') == b"Les conditions g\xc3\xa9n\xc3\xa9rales d'acc\xc3\xa8s s\xe2\x80\x99appliquent."
    assert len(ident.otherconstraints) == 2
    assert ident.spatialrepresentationtype[0] == 'vector'
    assert bytes(ident.title, 'utf-8') == b'Protection des captages - S\xc3\xa9rie'
    assert ident.topiccategory == ['geoscientificInformation', 'inlandWaters']
    assert ident.uricode == ['PROTECT_CAPT', '74f81503-8d39-4ec8-a49a-c76e0cd74946']
    assert ident.uricodespace == ['BE.SPW.INFRASIG.GINET', 'http://geodata.wallonie.be/id/']
    assert ident.useconstraints[0] == 'license'

def test_identification_contact(bmd):
    """ Tests CI_Responsibility class in indentification section
    """
    contact = bmd.identification[0].contact

    assert contact[0].email == 'helpdesk.carto@spw.wallonie.be'
    assert contact[0].organization[:21] == 'Helpdesk carto du SPW'
    assert contact[0].role == 'pointOfContact'

    assert bytes(contact[1].name, 'utf-8') == b'V\xc3\xa9ronique Willame'
    assert contact[1].organization[:31] == 'Direction des Eaux souterraines'
    assert contact[1].phone == '+32 (0)81/335923'
    assert contact[1].role == 'custodian'

    assert bytes(contact[2].onlineresource.description, 'utf-8') == b'G\xc3\xa9oportail de la Wallonie'
    assert contact[2].onlineresource.function == 'information'
    assert bytes(contact[2].onlineresource.name, 'utf-8') == b'G\xc3\xa9oportail de la Wallonie'
    assert contact[2].onlineresource.protocol == 'WWW:LINK'
    assert contact[2].onlineresource.url == 'https://geoportail.wallonie.be'
    assert contact[2].organization == 'Service public de Wallonie (SPW)'
    assert contact[2].role == 'owner'

def test_identification_date(bmd):
    """ Tests CI_Date class
    """
    date = bmd.identification[0].date
    assert date[0].date == '2000-01-01'
    assert date[0].type == 'creation'
    assert date[1].date == '2023-07-31'
    assert date[1].type == 'revision'
    assert date[2].date == '2022-11-08'
    assert date[2].type == 'publication'

def test_identification_extent(bmd):
    """ Tests EX_GeographicBoundingBox class
    """
    ident = bmd.identification[0]
    assert ident.denominators[0] == '10000'

    assert ident.extent.boundingBox.maxx == '6.50'
    assert ident.extent.boundingBox.maxy == '50.85'
    assert ident.extent.boundingBox.minx == '2.75'
    assert ident.extent.boundingBox.miny == '49.45'

    assert ident.bbox.maxx == '6.50'
    assert ident.bbox.maxy == '50.85'
    assert ident.bbox.minx == '2.75'
    assert ident.bbox.miny == '49.45'

def test_identification_keywords(bmd):
    """ Tests Keywords class
    """
    keyw = bmd.identification[0].keywords
    assert keyw[0].keywords[0].name == 'Sol et sous-sol'
    assert keyw[0].keywords[0].url == 'https://metawal.wallonie.be/thesaurus/theme-geoportail-wallon#SubThemesGeoportailWallon/1030'
    assert keyw[0].thesaurus['date'] == '2014-01-01'
    assert keyw[0].thesaurus['datetype'] =='publication'
    assert keyw[0].thesaurus['title'] == 'Thèmes du géoportail wallon'
    assert keyw[0].thesaurus['url'] == 'https://metawal.wallonie.be/thesaurus/theme-geoportail-wallon'
    assert keyw[0].type == 'theme'
    assert len(keyw[0].keywords) == 2
    assert len(keyw) == 5

def test_get_all_contacts(bmd):
    """ Test get_all_contacts()
    """
    conts = bmd.get_all_contacts()
    assert(len(conts) == 3)
    assert conts[0].role == 'pointOfContact'
    assert conts[1].role == 'custodian'
    assert conts[2].role == 'owner'


@pytest.fixture
def amd():
    """
    Create an MD_Metadata instance from AuScope 3D Models ISO 19115 Part 3 XML sample
    
    Source: https://portal.auscope.org.au/geonetwork
    """
    aust_sample = str(Path(__file__).parent.parent / "tests" / "resources" / "iso3_examples" / "auscope-3d-model.xml")
    with open(aust_sample, "r", encoding="utf-8") as f_d:
        xml_list = f_d.readlines()
        xml_str = ''.join(xml_list)
        xml_bytes = bytes(xml_str, encoding='utf-8')
        exml = etree.fromstring(xml_bytes)
        assert exml is not None
        return MD_Metadata(exml)

def test_aus(amd):
    """ Tests elements that are mostly not present in Belgian catchments sample
    """
    assert amd is not None
    ident = amd.identification[0]
    # Test 3D - vertical extents
    assert ident.extent.vertExtMax == '300'
    assert ident.extent.vertExtMin == '-400'
    # Test constraints & limitations
    assert ident.securityconstraints[0] == 'unclassified'
    assert ident.uselimitation[0] == 'https://creativecommons.org/licenses/by/4.0/'
    assert ident.accessconstraints[0] == 'license'
    assert ident.useconstraints[0] == 'license'
    # Test funder
    assert ident.funder[0].organization == 'AuScope'
    assert ident.funder[0].address == 'Level 2, 700 Swanston Street'
    assert ident.funder[0].city == 'Carlton'
    assert ident.funder[0].region == 'Victoria'
    assert ident.funder[0].country == 'Australia'
    assert ident.funder[0].postcode == '3053'
    assert ident.funder[0].email == 'info@auscope.org.au'
    # Test publisher
    assert ident.publisher[0].organization == 'Earth Resources Victoria'
    assert ident.publisher[0].phone == '1300 366 356'
    assert ident.publisher[0].address == 'GPO Box 2392'
    assert ident.publisher[0].city == 'Melbourne'
    assert ident.publisher[0].region == 'Victoria'
    assert ident.publisher[0].country == 'Australia'
    assert ident.publisher[0].postcode == '3001'
    assert ident.publisher[0].email == 'customer.service@ecodev.vic.gov.au'
    # Test creator
    assert ident.creator[0].name == 'P.B. SKLADZIEN'
    # Test contributor
    assert ident.contributor[0].name == 'C. Jorand'
    assert ident.contributor[1].name == 'A. Krassay'
    assert ident.contributor[2].name == 'L. Hall'
    # Test uricode
    assert ident.uricode[0] == 'https://geology.data.vic.gov.au/searchAssistant/document.php?q=parent_id:107513'


@pytest.fixture
def smd():
    """
    Create an MD_Metadata instance from Belgian health & safety ISO 19115 Part 3 XML services sample

    Source: https://metawal.wallonie.be/geonetwork
    """
    belgian_srv_sample = str(Path(__file__).parent.parent / "tests" / "resources" / "iso3_examples" / "metawal.wallonie.be-srv.xml")
    with open(belgian_srv_sample, "r", encoding="utf-8") as f_d:
        xml_list = f_d.readlines()
        xml_str = ''.join(xml_list)
        xml_bytes = bytes(xml_str, encoding='utf-8')
        exml = etree.fromstring(xml_bytes)
        assert exml is not None
        return MD_Metadata(exml)

def test_service(smd):
    """ Tests Belgian health & safety XML service record sample
    """
    assert smd is not None
    srv_ident = smd.identification[0]
    assert(isinstance(srv_ident, SV_ServiceIdentification))
    assert(srv_ident.type == 'view')
    assert(srv_ident.couplingtype == 'tight')
    assert(len(srv_ident.operations) == 0)
    assert(len(srv_ident.operateson) == 11)
    rec_2 = srv_ident.operateson[1]
    assert(rec_2['uuidref'] == '91f9ebb0-9bea-48b4-8572-da17450913b6')
    assert(rec_2['href'] == 'https://metawal.wallonie.be/geonetwork/srv/api/records/91f9ebb0-9bea-48b4-8572-da17450913b6')
    rec_9 = srv_ident.operateson[8]
    assert(rec_9['uuidref'] == '401a1ac7-7222-4cf8-a7bb-f68090614056')
    assert(rec_9['title'] == '[Brouillon] INSPIRE - Bruit des aéroports wallons (Charleroi et Liège) - Plan d’exposition au bruit en Wallonie (BE)')
    assert(rec_9['href'] == 'https://metawal.wallonie.be/geonetwork/srv/api/records/401a1ac7-7222-4cf8-a7bb-f68090614056')

@pytest.fixture
def emd():
    """
    Create a MD_Metadata instance from ESRI ArcGIS ISO 19115 Part 3 XML artificial sample
    This uses the older mdb v1 namespaces and has elements not present in other samples
    e.g. MD_Band

    Source: https://github.com/Esri/arcgis-pro-metadata-toolkit
    """
    arcgis_sample = str(Path(__file__).parent.parent / "tests" / "resources" / "iso3_examples" / "arcgis-sample.xml")
    with open(arcgis_sample, "r", encoding="utf-8") as f_d:
        xml_list = f_d.readlines()
        xml_str = ''.join(xml_list)
        xml_bytes = bytes(xml_str, encoding='utf-8')
        exml = etree.fromstring(xml_bytes)
        assert exml is not None
        return MD_Metadata(exml)

def test_md_featurecataloguedesc(emd):
    """ Tests MD_FeatureCatalogueDescription
    """
    assert emd is not None
    cont_info = emd.contentinfo[0]
    assert cont_info.compliancecode == True
    assert cont_info.includedwithdataset == True
    assert cont_info.featurecatalogues[0] == "Resource > Content > Feature Catalogue > Feature Catalogue Citation > Titles > Title"
    assert cont_info.featuretypenames[0] == "Resource > Content > Feature Catalogue > Feature Type > Name"
    assert cont_info.language == ['fre']

def test_md_imagedescription(emd):
    """ Tests MD_ImageDescription and MD_Band
    """
    img_desc = emd.contentinfo[1]
    assert img_desc.type == 'image'
    assert img_desc.attributedescription == "Resource > Content > Image Description > Attribute Description"
    assert img_desc.cloudcover == '6.5'
    assert img_desc.processinglevel == "Resource > Content > Image Description > Processing Level Code > Code"
    assert img_desc.bands[0].id == "Resource > Content > Image Description > Band > Sequence Identifier"
    assert img_desc.bands[0].units == "Unified Code of Units of Measure"
    assert img_desc.bands[0].max == '255.99'
    assert img_desc.bands[0].min == '0.01'

def test_dq_dataquality(emd):
    """ Tests DQ_DataQuality
    """
    dq = emd.dataquality
    assert dq.conformancetitle[0][:90] == "Resource > Data Quality > Report > Conformance Result > Specification > Titles > Title (Ty"
    assert dq.conformancedate[0] == '2010-07-01T00:00:00'
    assert dq.conformancedatetype[0] == 'creation'
    assert dq.conformancedegree[0] == 'true'
    assert dq.lineage == None  # emd does not have lineage within DQ_DataQuality
    assert dq.lineage_url == None
    assert dq.specificationtitle == 'Resource > Data Quality > Report > Conformance Result > Specification > Titles > Title (Type=Domain Consistency)'
    assert dq.specificationdate[0] == '2010-07-01T00:00:00'

def test_md_reference_system(emd):
    """ Tests MD_ReferenceSystem
    """
    assert emd.referencesystem.code == 'Resource > Spatial Reference > Reference System > Code'
    assert emd.referencesystem.codeSpace == 'Resource > Spatial Reference > Reference System > Code Space'
    assert emd.referencesystem.version == 'Resource > Spatial Reference > Reference System > Version'

def test_service2(emd):
    """ Tests SV_ServiceIdentification fields not present in other sources
    """
    srv_ident = emd.identification[0]
    assert(isinstance(srv_ident, SV_ServiceIdentification))
    assert(srv_ident.type == "Resource > Service Details > Service Type > Name")
    assert(srv_ident.version == "Resource > Service Details > Service Type Version")
    assert(srv_ident.couplingtype == 'loose')
    assert(srv_ident.fees == "Resource > Service Details > Access Properties > Fees")

def test_md_distribution(emd):
    """ Test MD_Distribution
    """
    contact = emd.distribution.distributor[0].contact
    assert contact.address =='Resource > Distribution > Distributor > Contact Information > Address'
    assert contact.city =='Resource > Distribution > Distributor > Contact Information > City'
    assert contact.email =='Resource > Distribution > Distributor > Contact Information > Email'
    assert contact.organization =='Resource > Distribution > Distributor > Organization'
    assert contact.phone =='Resource > Distribution > Distributor > Contact Information > Phone'
    assert contact.postcode =='Resource > Distribution > Distributor > Contact Information > Postal Code'
    assert contact.region =='Resource > Distribution > Distributor > Contact Information > State'
    assert contact.role =='distributor'
    online = emd.distribution.online[0]
    assert online.protocol == 'Resource > Distribution > Digital Transfer Options > Online Resource > Protocol'
    assert online.url == 'http://Resource_Distribution_Digital_Transfer_Options_Online_Resource_Linkage'


