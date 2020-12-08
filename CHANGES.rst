Changes
=======

0.21.0 (2020-12-09)
-------------------

A full list of commits for 0.21.0 can be found at:

https://github.com/geopython/OWSLib/commits/0.21.0

- OGC API: Added support for Coverages (#699)
- WFS: Added POST support to WFS GetFeature (#706)
- WCS: Allow user to specify timeout on WCS GetCoverage calls (#714)
- WPS: fixed bounding-box (#719)
- Various fixes: #695, #707, #702, #716, #718, #722, #691, #720

0.20.0 (2020-06-05)
-------------------

This release provides initial support for the draft OGC API - Records
standard.

A full list of commits for 0.20.0 can be found at:

https://github.com/geopython/OWSLib/commits/0.20.0

- WFS: make wfs:FeatureTypeList optional for 1.1 and 2.0 (#673)
- OGC API - Records: initial draft implementation (#679, #693)
- WPS: add support for retrieving data from local filesystem (huard, #681)
- WMTS: add support for boundingboxes (kordian-kowalski, #687)
- Authentication: Enable switching off SSL verification (Samweli, #685)


0.19.2 (2020-03-13)
-------------------

This release is an update.
It drops Python 3.5 support and adds language support to the WPS module.

A full list of commits for 0.19.2 can be found at:

https://github.com/geopython/OWSLib/commits/0.19.2

- Dropped Python 3.5 support (#659).
- Fix pyproj deprecation (only use pyproj>=2) (#661).
- WPS: Added support for multiple languages (#654, #655).
- OGC API: fix api media type handling (#653).
- WMTS: fix cartopy examples (#656).
- Tests: fix wms tests (#657).
- WCS: added WCS code example do documentation (#658).
- WCS: fix params list (#663).

0.19.1 (2020-01-29)
-------------------

This release is an update with a fix for Python 3.8 installation.

A full list of commits for 0.19.1 can be found at:

https://github.com/geopython/OWSLib/commits/0.19.1

- Fixed Python 3.8 installation (#635, ocefpaf)
- Refactored OGC API (#641, tomkralidis)
- Add `python_requires` to prevent pip installing this on Python 2.x (#634, craigds)
- Tests: use HEAD instead of GET in service_ok (#651, roel)
- Tests: replaced service URLs with working versions (#648, roel)
- WFS: Fix WFS get_schema when typename doubles as attributename (#647, roel)
- WCS: Removed redundant check on logging level (#646, johanvdw)
- WFS3: renamed time parameter to datetime (#639, mattfung)
- WFS: Added required fields to wfs schema (#628, Alexandre27)
- WCS: added resolution and size params to WCS GetCoverage requests (#633, dukestep)
- DOCS: updated WMS docs (#649, pathmapper)

0.19.0 (2019-11-14)
-------------------

Python 2 support has been removed.  Users are strongly encouraged to
upgrade to the latest version of OWSLib and Python 3.

A full list of commits for 0.19.0 can be found at:

https://github.com/geopython/OWSLib/commits/0.19.0

- ALL: 2 support removed (cehbrecht et. al.)
- OWS
- safeguard ProviderSite/@href (jannefleischer)
- safeguard bbox parsing (walkermatt)
- WMS: support ScaleDenominator
- WMTS: add timeout (jachym)
- OGC API
- Features updates following specification
- TMS: fix broken constructor (justb4)
- ALL: pass HTTP headers for WMS/WFS/WMTS/TMS (justb4)
- ALL: test fixes/updates

0.18.0 (2019-06-24)
-------------------

This release includes initial support for the evolving OGC API - Features
standard (aka WFS 3), which represents a clean break from the traditional
design patterns of OGC interface specifications.  This release also includes
a refactoring of authentication support into a common approach for all parts of the codebase to use.
Thanks to Eric Spitler for this enhanced functionality!

Users are strongly encouraged to use OWSLib via Python 3 as Python 2 support
(Travis, python-six) will be removed in the future.

A full list of commits for 0.18.0 can be found at:

https://github.com/geopython/OWSLib/commits/0.18.0

- NEW: WFS 3 initial implementation
- NEW: add Authentication framework (eric-spitler)
- WPS:
    * add process properties, percentCompleted (cehbrecht)
    * add reference attributes (enolfc)
    * add support for multi process processes (huard)
- OWS: add support for crs and dimension (saimeCS)

0.17.1 (2019-01-12)
-------------------

Bugfix release for issues in WPS and WMS.

A full list of commits for 0.17.1 can be found at:

https://github.com/geopython/OWSLib/commits/0.17.1

0.17.0 (2018-09-04)
-------------------

This release provides numerous fixes, enhancements and re-engineering
of OWSLib's test framework.

A full list of commits for 0.17.0 can be found at:

https://github.com/geopython/OWSLib/commits/0.17.0

- NEW: OWS Context implementation (#483 allixender)
- ISO:
    * Added MD_LegalConstraints to uselimitation xpath (m431m)
    * Fix ISO metadata parsing for empty gmd:featureCatalogueCitation. (Roel)
- OWS:
    * Improve remote metadata parsing (Roel)
    * Allow the lack of optional ows:ServiceProvider (mhugo)
- WPS:
    * add headers, cert options (cehbrecht)
    * add lineage to execute (cehbrecht)
- WMTS/TMS: replaced ServiceMetadata (cehbrecht)
- SOS: fix encoding error (cehbrecht)
- tests: move away from doctests (#339 cehbrecht)
- overall codebase: move from pep8 to flake8
- Support for WCS 2.0.0 and 2.0.1 (#430, thanks @doclements)

0.16.0 (2017-12-21)
-------------------

- drop Python 2.6 support
- WFS: get schema auth params (karakostis)
- WFS: add sortby to GetFeature requests (drnextgis)
- CSW: add ows namespace to bounding box queries
- CSW: add feature catalogue support parsing
- CRS: support proj.4 CRS definitions (orhygine)
- fix namespaces (jsanchezfr)
- ISO GM03: fix bounding box handling

0.15.0 (2017-09-13)
-------------------

- WFS:
    * add doseq to WFS request qyery urlencode
    * handle non-existing bounding boxes in feature types
- SOS:
    * add support for authentication
- WMTS:
    * add support for styles
- ISO:
    * add support for gmd:locale
- GM03:
    * add support for GM03 ISO metadata profile
- CRS:
    * catch invalid CRS codes
- WMS:
    * fix time dimension handling in Capabilities
- SWE:
    * various bug fixes
- WPS:
    * fix WPS DescribeProcess issue on DataType
    * fixed bbox lower/upper_corner conversion
    * added a test for wps BoundingBoxDataInput
    * added BoundingBoxDataInput and fix boundingbox parsing
- Misc:
    * fix double ``&&`` in URL requests
    * add util.clean_ows_url function to remove basic service parameters from OWS base URLs

0.14.0 (2017-01-12)
-------------------

- WFS: add authentication (@pmauduit)
- WFS: fix parameter names for WFS2
- OWS: implement updateSequence support
- CSW: fix ref bug in CSW-T workflows
- WCS: fix 1.0.0 Capabilities OWS namespace handling

0.13.0 (2016-09-24)
-------------------

- general: Handle servers that give 500 errors better (@davidread)
- WMS: 1.3.0 support @roomthily / @b-cube
- WMS: add WMS request property to cache request URL, add service parameter
- OWS: add ows.ServiceIdentification.versions, fix ref in ows.ServiceIdentification.profiles

0.12.0 (2016-09-12)
-------------------

- OWS: Support OWS Constraints and Parameters
- SOS/WaterML: handle WaterML 2.0 updates and SOS decoder
- Add username and password arguments to WFS class constructors

0.11.0 (2016-04-01)
-------------------

- CSW: fix outputschema setting when raw XML is specified
- ISO:
    * parsing anchor for abstract and lineage fields added (madi)
    * added support for spatialRepresentationType (pmdias)
    * add MD_Keywords class (pmdias)
    * fix md.languagecode to come from the codeListValue attribute (pmdias)
- WFS: add get_schema method for DescribeFeatureType parsing (jachym)
- WMS: do not assume parent layers should be queryable if 1..n of their children is
- WMTS: fix parsing when ServiceProvider does not exist
- WPS:
    * fix bbox type, parsing bbox output (cehbrecht)
    * add support for bbox data and more robust literal data parsing (jachym)

0.10.0 (2015-11-11)
-------------------

- GM03: add support for GM03 metadata
- WPS: add fix for optional Abstract

0.9.2 (2015-09-23)
------------------

- etree: add convenience function to report which etree is used
- WMS: add GetFeatureInfo support (JuergenWeichand)
- WMS: add a children attribute to ContentMetadata to handle WMS nested layers (Jenselme)
- WMTS: add support for restful only WMTS (JuergenWeichand)
- pass headers to requests (ayan-usgs)

0.9.1 (2015-09-03)
------------------

- etree: Fix incorrect lxml ParseError import (daf)
- CRS: make crs hashable (QuLogic)
- WPS:
    * statuslocation bugfix (dblodgett-usgs)
    * various bugfixes, tests and examples (cehbrecht)
- WFS:
    * fix WFS 2.0 stored queries bugfix (JuergenWeichand)
    * add docs for WFS 1.1/2.0 (JuergenWeichand)
- ISO: ignored empty gmd:identificationInfo elements (menegon)

0.9.0 (2015-06-12)
------------------

- Python 3 compatibility (numerous contributors!)
- CSW:
    * fix Capabilities parsing when ows:ServiceProvider is empty
    * fix GetRecordById URL
- WCS: add support for 1.1.1 (ldesousa)
- ISO:
    * add support for gmd:MD_ReferenceSystem (kalxas)
    * safeguard vars (dblodgett-usgs)
- SOS: add sa namespace, add procedure as optional parameter (ict4eo)

0.8.13 (2015-02-12)
-------------------

- SOS: fix var reference blocker (ocefpaf)
- various Python 3 enhancements

0.8.11 (2014-12-17)
-------------------

- WMTS: add/fix vendor kwarg handling (rhattersley)
- WMS: add ScaleHint support (SiggyF)
- FES: add srsName support for gml:Envelope, add filter to string support
- WFS: add timeout support (selimnairb), add support for startindex
- fix/cleanup tests

0.8.10 (2014-10-13)
-------------------

- CSW: fix bad URL being sent to GetRecords
- SOS: add timeout support (lukecampbell)
- WPS: add logging (dblodgett-usgs)
- WFS: ignore comments when parsing (Samuli Vuorinen)
- tests: add support for logging
- LICENSE: update reference (johanvdw )

0.8.9 (2014-09-24)
-------------------------

- CSW: support ``gmi:MI_Metadata`` as ``gmd:MD_Metadata`` when parsing reuslts (@FuhuXia)
- CSW: add support for basic authentication
- ISO: add support for instantiation of MD_Metadata objects (@kalxas)
- ISO: add support for CI_ResponsibleParty as a responsible role attribute (@milokmet)
- ISO: add title support for SV_ServiceIdentification (@dblodgett-usgs)
- SOS: add 'om' back to namespace list (@ict4eo)
- util: add support for race conditions for WPS (@TobiasKipp)

0.8.8 (2014-07-05)
------------------

- CSW: use URLS as defined in GetCaps for CSW operations (@kwilcox)
- CSW: fix GetRecordById (@kwilcox)
- CSW: use default CSW URL when initialized with skip_caps=True
- WMTS: Allow vendor-specific args in WMTS tile requests (@rhattersley)
- ISO: allow for MD_Metadata to be intialized as empty, supporting export to XML functionality (@kalxas)
- ISO: add support for gmd:RS_Identifier needed by INSPIRE (@kalxas)
- numerous unit test / build fixes and cleanups

0.8.7 (2014-05-02)
------------------

- WPS: add method to write output to disk (@ldesousa)
- CSW: add method to get operations by name
- CSW: responses now maintain order using OrderedDict
- CSW: ensure namespace is declared for GetRecords typeName values in request (@kwilcox)
- SOS: fix error detections (@daf)
- ISO: fix xpath for selecting gmd:thesaurusName (@menegon)
- add timeouts to HTTP functions (@iguest)
- FES: add matchCase to ogc:PropertyIsLike
- logging: add Null handler to not write files randomly (@kwilcox)
- WFS: add GetFeature outputformat support (@kwilcox, @rsignell-usgs)
- ISO: support GML 3.2 extent handling
- numerous unit test / build fixes and cleanups

0.8.3 (2014-01-10)
------------------

- allow CSW URLs to be requested as unicode or string (@rclark)
- support multiple gmd:extent elements (@severo)
- support WMS default time position (@vicb)
- fix SOS GetCapabilities support (@kwilcox)
- support missing CSW nextRecord (@davidread)
- use child layers for WMS duplicates
- numerous unit test fixes and cleanups

0.8.0 (2013-09-11)
------------------

- Support for WaterML 1.0 and 1.1 (thanks @kwilcox and @CowanSM)
- drastically improved CSW getrecords support (owslib.csw.CatalogueServiceWeb.getrecords2, which will eventually replace owslib.csw.CatalogueServiceWeb.getrecords, which is now deprecated) (thanks @kwilcox and @rsignell-usgs input)
- fix owslib.csw.CatalogueServiceWeb to use HTTP GET for GetCapabilities and GetRecordById (thanks @rsignell-usgs for input)
- numerous test fixes
- support owslib.iso.MD_Metadata scanning of multiple extents (thanks @severo)
- add WMS elevation support in Capabilities (thanks @mhermida)
- travis-ci setup (thanks @brianmckenna)
- Support for TMS (thanks @cleder)
- updated build packages (thanks @kalxas)
- numerous bug fixes

0.7 (2013-02-18)
----------------

- Support for SOS 1.0.0, SOS 2.0.0, SensorML (thanks @kwilcox)
- Support for TMS (thanks @cleder)
- numerous bug fixes

0.6 (2012-12-22)
----------------

- Support for WMTS (thanks @bradh)
- packaging support (thanks @kalxas) for:
    * openSUSE
    * Debian
- addition of owslib.__version__
- ISO support:
    * multiple gmd:identificationInfo elements
    * gmd:distributorInfo elements
- WMS
    * read additional Layer attributes (thanks @elemoine)
- numerous bug fixes

0.5 (2012-06-15)
----------------

- Support for the following parsers:
    * WPS 1.0.0
    * WFS 1.1.0
    * CRS handling: URNs, URIs, EPSG:xxxx style
- etree.py looks for lxml.etree first now
- catch WMS service exceptions on GetCapabilities
- CSW exceptions are now Pythonic

0.4 (2011-10-02)
----------------

- Support for the following parsers:
    * CSW 2.0.2
    * OWS Common 1.0.0, 1.1.0, 2.0.0
    * Filter Encoding 1.1.0
    * ISO 19115:2003
    * FGDC CSDGM
    * NASA DIF
    * Dublin Core
    * WFS 2.0
    * WCS 1.1
- New SCM/bug/mailing list infrastructure
- Sphinx documentation

0.3 (2008-05-08)
----------------

- WCS support.
- Support for basic authorization in WMS requests (#107).

0.2.1 (2007-08-06)
------------------

- Added support for Python 2.5.
- Fixed ticket #105: Don't depend on Content-length in the http headers for
  getfeature.

0.2.0 (2007-02-01)
------------------

- Change license to BSD.
- Added service contact metadata.

0.1.0 (2006-10-19)
------------------

- New and improved metadata API.
- Wrappers for GetCapabilities, WMS GetMap, and WFS GetFeature requests.
- Doctests.

0.0.1 (2006-07-30)
------------------

- Brought OWSLib up out of the PCL trunk into its own space.
- Updated the testing frameworm.
- Initial test coverage:

.. csv-table:: Test Coverage
   :header: "Name", "Stmts", "Exec", "Cover", "Missing"
   :widths: 5, 5, 5, 5, 20

   "wms", 105, 68, 64%, "36, 41-48, 61-63, 114-118, 125-155, 172, 203-205"
   "wfs", 74, 69, 93%, "146, 166, 199-201"
   "wmc", 111, 0, 0%, "33-220"
   "TOTAL", 290, 137, 47%, ""
