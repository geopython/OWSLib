# -*- coding: utf-8 -*-
# =============================================================================
# Authors : Alexander Kmoch <allixender@gmail.com>
#
# =============================================================================

"""
API for OGC Web Services Context Document (OWS Context) format.

Conceptual model base classes: http://www.opengeospatial.org/standards/owc

OGC OWS Context Conceptual Model 1.0 (12-080r2)
"""

from __future__ import (absolute_import, division, print_function)

from owslib.owscontext.atom import decode_atomxml, encode_atomxml
from owslib.owscontext.common import GENERIC_OWCSPEC_URL
# from owslib.util import log
# TODO make dates from (currently) string to datetime instances
from owslib.owscontext.common import TimeIntervalFormat
from owslib.owscontext.common import try_float, try_int, \
    extract_p, build_from_xp
from owslib.owscontext.geojson import encode_json, decode_json


class OwcContext(object):
    """
    * + specReference :URI
    * + language :CharacterString
    * + id :CharacterString
    * + title :CharacterString
    * + abstract :CharacterString [0..1]
    * + updateDate :CharacterString [0..1]
    * + author :CharacterString [0..*]
    * + publisher :CharacterString [0..1]
    * + creator :Creator [0..1]
    * +----+ creatorApplication :CreatorApplication [0..1]
    * +----+ creatorDisplay :CreatorDisplay [0..1]
    * + rights :CharacterString [0..1]
    * + areaOfInterest :GM_Envelope [0..1]
    * + timeIntervalOfInterest :TM_GeometricPrimitive [0..1]
    * + keyword :CharacterString [0..*]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 id,
                 update_date,
                 title,
                 language="en",
                 spec_reference=[],
                 area_of_interest=[],
                 context_metadata=[],
                 subtitle=None,
                 authors=[],
                 publisher=None,
                 creator_application=None,
                 creator_display=None,
                 rights=None,
                 time_interval_of_interest=None,
                 keywords=[],
                 resources=[]
                 ):
        """
        constructor:

        :param id: URL
        :param update_date: datetime
        :param title:   String,
        :param language: String = "en"
        :param spec_reference: OwcLink[]  links.profiles[] and rel=profile
        :param area_of_interest: Option[Rectangle] = None, aka Double[]
        :param context_metadata: OwcLink[] links.via[] and rel=via
        :param subtitle: Option[String] = None,
        :param authors: List[OwcAuthor]
        :param publisher: Option[String] = None,
        :param creator_application: Option[OwcCreatorApplication] = None,
        :param creator_display: Option[OwcCreatorDisplay] = None,
        :param rights: Option[String] = None,
        :param time_interval_of_interest: TimeIntervalFormat(start,end)
        :param keywords: OwcCategory[]
        :param resources: OwcResource[]
        """
        self.id = id
        self.spec_reference = spec_reference
        self.area_of_interest = area_of_interest
        self.context_metadata = context_metadata
        self.language = language
        self.title = title
        self.subtitle = subtitle
        self.update_date = update_date
        self.authors = authors
        self.publisher = publisher
        self.creator_application = creator_application
        self.creator_display = creator_display
        self.rights = rights
        self.time_interval_of_interest = time_interval_of_interest
        self.keywords = keywords
        self.resources = resources

        # TODO spec reference, check or provide?
        if len(self.spec_reference) <= 0:
            self.spec_reference.append(
                OwcLink(href=GENERIC_OWCSPEC_URL, rel='profile'))

        # TODO check and validate? how much?

    def to_dict(self):
        """

        :return: dict of obj
        """
        return {
            "type": "FeatureCollection",
            "id": self.id,
            "bbox": self.area_of_interest,
            "properties": {
                "lang": self.language,
                "title": self.title,
                "abstract": self.subtitle,
                "updated": self.update_date,
                "date":
                    None if self.time_interval_of_interest is None else
                    self.time_interval_of_interest.__str__(),
                "rights": self.rights,
                "authors":
                    [] if len(self.authors) <= 0 else
                    [obj.to_dict() for obj in self.authors],
                "publisher": self.publisher,
                "display":
                    None if self.creator_display is None else
                    self.creator_display.to_dict(),
                "generator":
                    None if self.creator_application is None else
                    self.creator_application.to_dict(),
                "categories":
                    [] if len(self.keywords) <= 0 else
                    [obj.to_dict() for obj in self.keywords],
                "links": {
                    "profiles":
                        [] if len(self.spec_reference) <= 0 else
                        [obj.to_dict() for obj in self.spec_reference],
                    "via":
                        [] if len(self.context_metadata) <= 0 else
                        [obj.to_dict() for obj in self.context_metadata]
                    },
            },
            "features":
                [] if len(self.resources) <= 0 else
                [obj.to_dict() for obj in self.resources]
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        # TODO add spec url conversion from generic to geojson
        return encode_json(self.to_dict())

    def to_atomxml(self):
        # TODO add spec url conversion from generic to atom
        return encode_atomxml(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        # TODO parse bbox??
        return OwcContext(
            id=d['id'],
            spec_reference=[OwcLink.from_dict(do) for do in
                            extract_p('properties.links.profiles', d, [])],
            area_of_interest=extract_p('bbox', d, None),
            context_metadata=[OwcLink.from_dict(do) for do in
                              extract_p('properties.links.via', d, [])],
            language=extract_p('properties.lang', d, None),
            title=extract_p('properties.title', d, None),
            subtitle=extract_p('properties.abstract', d, None),
            update_date=extract_p('properties.updated', d, None),
            authors=[OwcAuthor.from_dict(do) for do in
                     extract_p('properties.authors', d, [])],
            publisher=extract_p('properties.publisher', d, None),
            creator_application=build_from_xp(
                'properties.generator', d, OwcCreatorApplication, None),
            creator_display=build_from_xp(
                'properties.display', d, OwcCreatorDisplay, None),
            rights=extract_p('properties.rights', d, None),
            time_interval_of_interest=TimeIntervalFormat.from_string(
                extract_p('properties.date', d, None)),
            keywords=[OwcCategory.from_dict(do) for do in
                      extract_p('properties.categories', d, [])],
            resources=[OwcResource.from_dict(do) for do in
                       extract_p('features', d, [])]
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        # TODO add spec url conversion from geojson to generic
        # TODO should validate if geojson Type == FeatureCollection?
        return cls.from_dict(d)

    @classmethod
    def from_atomxml(cls, xml_bytes):
        """
        lets see if we can reuse the dict structure builder from geojson
        :param xmlstring:
        :return: OwcContext
        """
        # TODO add spec url conversion from atom to generic
        # TODO should validate anything?
        # TODO ValueError: Unicode strings with encoding declaration
        # are not supported. Please use bytes input or XML fragments
        # without declaration -> Decide, currently bytes
        d = decode_atomxml(xml_bytes)
        return cls.from_dict(d)


class OwcResource(object):
    """
    * + id :CharacterString -
        Unambiguous reference to the identification of the resource,
        SHALL contain an (IRI) URI value
    * + title :CharacterString
    * + abstract :CharacterString [0..1]
    * + updateDate :TM_Date [0..1]
    * + author :CharacterString [0..*]
    * + publisher :CharacterString [0..1]
    * + rights :CharacterString [0..1]
    * + geospatialExtent :GM_Envelope [0..1]
    * + temporalExtent :TM_GeometricPrimitive [0..1]
    * + contentDescription :Any [0..1] // aka alternates
    * + preview :URI [0..*]
    * + contentByRef :URI [0..*]
    * + offering :Offering [0..*]
    * + active :Boolean [0..1]
    * + keyword :CharacterString [0..*]
    * + maxScaleDenominator :double [0..1]
    * + minScaleDenominator :double [0..1]
    * + folder :CharacterString [0..1]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 id,
                 title,
                 update_date,
                 subtitle=None,
                 authors=[],
                 publisher=None,
                 rights=None,
                 geospatial_extent=None,
                 temporal_extent=None,
                 content_description=[],
                 preview=[],
                 content_by_ref=[],
                 offerings=[],
                 active=False,
                 resource_metadata=[],
                 keywords=[],
                 min_scale_denominator=None,
                 max_scale_denominator=None,
                 folder=None
                 ):
        """
        constructor:

        :param id: URL
        :param title: String
        :param update_date: datetime
        :param subtitle: String
        :param authors: List[OwcAuthor]
        :param publisher: String
        :param rights: String
        :param geospatial_extent: currently GeoJSON Polygon String
        :param temporal_extent: str
        :param content_description: OwcLink[] links.alternates, rel=alternate
        :param preview: OwcLink[] aka links.previews[] and rel=icon (atom)
        :param content_by_ref: OwcLink[], links.data, rel=enclosure (atom)
        :param offerings: OwcOffering[]
        :param active: Boolean
        :param resource_metadata: OwcLink[] aka links.via[] & rel=via
        :param keywords: OwcCategory[]
        :param min_scale_denominator: Double
        :param max_scale_denominator: Double
        :param folder: String
        """
        # # TimeIntervalFormat(start,end)
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.update_date = update_date
        self.authors = authors
        self.publisher = publisher
        self.rights = rights
        self.geospatial_extent = geospatial_extent
        self.temporal_extent = temporal_extent
        self.content_description = content_description
        self.preview = preview
        self.content_by_ref = content_by_ref
        self.offerings = offerings
        self.active = active
        self.resource_metadata = resource_metadata
        self.keywords = keywords
        self.min_scale_denominator = min_scale_denominator
        self.max_scale_denominator = max_scale_denominator
        self.folder = folder

    def to_dict(self):
        # TODO parse geometry??
        return {
            "type": "Feature",
            "id": self.id,
            "geometry": self.geospatial_extent,
            "properties": {
                "title": self.title,
                "abstract": self.subtitle,
                "updated": self.update_date,
                "date":
                    None if self.temporal_extent is None else
                    self.temporal_extent.__str__(),
                "authors":
                    [] if len(self.authors) <= 0 else
                    [obj.to_dict() for obj in self.authors],
                "publisher": self.publisher,
                "rights": self.rights,
                "categories":
                    [] if len(self.keywords) <= 0 else
                    [obj.to_dict() for obj in self.keywords],
                "links": {
                    "alternates":
                        [] if len(self.content_description) <= 0 else
                        [obj.to_dict() for obj in
                         self.content_description],
                    "previews":
                        [] if len(self.preview) <= 0 else
                        [obj.to_dict() for obj in self.preview],
                    "data":
                        [] if len(self.content_by_ref) <= 0 else
                        [obj.to_dict() for obj in
                         self.content_by_ref],
                    "via":
                        [] if len(self.resource_metadata) <= 0 else
                        [obj.to_dict() for obj in
                         self.resource_metadata]
                    },
                "offerings":
                    [] if len(self.offerings) <= 0 else
                    [obj.to_dict() for obj in self.offerings],
                "active": self.active,
                "minscaledenominator": self.min_scale_denominator,
                "maxscaledenominator": self.max_scale_denominator,
                "folder": self.folder
            }
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcResource(
            id=d['id'],
            geospatial_extent=extract_p('geometry', d, None),
            title=d['properties']['title'],
            subtitle=extract_p('properties.abstract', d, None),
            update_date=extract_p('properties.updated', d, None),
            authors=[OwcAuthor.from_dict(do) for do in
                     extract_p('properties.authors', d, [])],
            publisher=extract_p('properties.publisher', d, None),
            rights=extract_p('properties.rights', d, None),
            temporal_extent=TimeIntervalFormat.from_string(
                extract_p('properties.date', d, None)),
            keywords=[OwcCategory.from_dict(do) for do in
                      extract_p('properties.categories', d, [])],
            resource_metadata=[OwcLink.from_dict(do) for do in
                               extract_p('properties.links.via', d, [])],
            content_description=[OwcLink.from_dict(do)
                                 for do in extract_p(
                    'properties.links.alternates', d, [])],
            preview=[OwcLink.from_dict(do) for do in
                     extract_p('properties.links.previews', d, [])],
            content_by_ref=[OwcLink.from_dict(do) for do in
                            extract_p('properties.links.data', d, [])],
            offerings=[OwcOffering.from_dict(do) for do in
                       extract_p('properties.offerings', d, [])],
            active=extract_p('properties.active', d, None),
            min_scale_denominator=try_float(extract_p(
                'properties.minscaledenominator', d, None)),
            max_scale_denominator=try_float(extract_p(
                'properties.maxscaledenominator', d, None)),
            folder=extract_p('properties.folder', d, None),
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        # TODO should validate if geojson Type == Feature?
        return cls.from_dict(d)


class OwcCreator(object):
    """
    * + creatorApplication :CreatorApplication [0..1]
    * + creatorDisplay :CreatorDisplay [0..1]
    * + extension :Any [0..*]
    *
    * OWCCreator base class is never realized by itself,
        neither in Atom nor in GeoJSON Encoding;
    * Creator/Display and Creator/Application are instantiated as completely
        separate entities in both Atom and GeoJSON
    """

    def __init__(self,
                 creator_application=None,
                 creator_display=None
                 ):
        """
        constructor:

        :param creator_application: OwcCreatorApplication
        :param creator_display: OwcCreatorDisplay
        """
        self.creator_application = creator_application
        self.creator_display = creator_display


class OwcCreatorApplication(object):
    """
    CreatorApplication
    + title :CharacterString [0..1]
    + uri :URI [0..1]
    + version :Version [0..1]
    + the single only class that doesn't have explicit extension?
        (but would be inherited from OWC:Creator?)
    """

    def __init__(self,
                 title,
                 uri=None,
                 version=None
                 ):
        """
        constructor:

        :param title: String
        :param uri: URL
        :param version: String
        """
        self.title = title
        self.uri = uri
        self.version = version

    def to_dict(self):
        return {
            "title": self.title,
            "uri": self.uri,
            "version": self.version
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcCreatorApplication(
            title=extract_p('title', d, None),
            uri=extract_p('uri', d, None),
            version=extract_p('version', d, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcCreatorDisplay(object):
    """
    CreatorDisplay
    + pixelWidth :int [0..1]
    + pixelHeight :int [0..1]
    + mmPerPixel :double [0..1]
    + extension :Any [0..*]
    """

    def __init__(self,
                 pixel_width,
                 pixel_height=None,
                 mm_per_pixel=None,
                 ):
        """
        constructor:

        :param pixel_width: Double
        :param pixel_height: Double
        :param mm_per_pixel: Double
        """
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.mm_per_pixel = mm_per_pixel

    def to_dict(self):
        return {
            "pixelWidth": self.pixel_width,
            "pixelHeight": self.pixel_height,
            "mmPerPixel": self.mm_per_pixel
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcCreatorDisplay(
            pixel_width=try_int(extract_p('pixelWidth', d, None)),
            pixel_height=try_int(extract_p('pixelHeight', d, None)),
            mm_per_pixel=try_float(extract_p('mmPerPixel', d, None))
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcLink(object):
    """
    * OwcLink in most cases will have an array of links at the path of the rel
    *
    * OWC:Context specReference attribute:
        atom rel="profile" - geojson links.profiles[] array
    * OWC:Context contextMetadata attribute:
        atom rel="via" - geojson links.via[] array
    *
    * OWC:Resource contentDescription attribute:
        atom rel="alternate" - geojson links.alternates[] array
    * OWC:Resource preview attribute:
        atom rel="icon" - geojson links.previews[] array
    * OWC:Resource contentByRef attribute:
        atom rel="enclosure" - geojson links.data[] array
    * OWC:Resource resourceMetadata attribute:
        atom rel="via" - geojson links.via[] array
    *
    * links for data and previews
        (aka rels enclosure and icon should have length attributes set)
    *
    * + href :URI
    * + type :String [0..1]
    * + lang :String [0..1]
    * + title :String [0..1]
    * + length :Integer [0..1]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 href,
                 rel,
                 mimetype=None,
                 lang=None,
                 title=None,
                 length=None,
                 ):
        """
        constructor:

        :param href: URL
        :param rel: String
        :param mimetype: String
        :param lang: String
        :param title: String
        :param length: Int
        """
        self.href = href
        self.rel = rel
        self.mimetype = mimetype
        self.lang = lang
        self.title = title
        self.length = length

    def to_dict(self):
        return {
            "href": self.href,
            "type": self.mimetype,
            "length": self.length,
            "lang": self.lang,
            "title": self.title,
            "rel": self.rel
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcLink(
            href=extract_p('href', d, None),
            rel=extract_p('rel', d, None),
            mimetype=extract_p('type', d, None),
            lang=extract_p('lang', d, None),
            title=extract_p('title', d, None),
            length=try_int(extract_p('length', d, None))
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcCategory(object):
    """
    keywords class
    """

    def __init__(self,
                 term,
                 scheme=None,
                 label=None,
                 ):
        """
        constructor:

        :param term: String
        :param scheme: String (can point to a controlled list, too, I guess)
        :param label: String
        """
        self.term = term
        self.scheme = scheme
        self.label = label

    def to_dict(self):
        return {
            "scheme": self.scheme,
            "term": self.term,
            "label": self.label
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcCategory(
            term=extract_p('term', d, None),
            scheme=extract_p('scheme', d, None),
            label=extract_p('label', d, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcAuthor(object):
    """
    apparently handled differently in Atom and GeoJSON encodings?
    """

    def __init__(self,
                 name=None,
                 email=None,
                 uri=None
                 ):
        """
        constructor:

        :param name: String
        :param email: String (EmailAddress)
        :param uri: URL
        """
        self.name = name
        self.email = email
        self.uri = uri

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "uri": self.uri
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcAuthor(
            name=extract_p('name', d, None),
            email=extract_p('email', d, None),
            uri=extract_p('uri', d, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcOffering(object):
    """
    * + code :URI
    * + operations :Offering [0..*]
    * + contents :Content [0..*]
    * + styles :StyleSet [0..*]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 offering_code,
                 operations=[],
                 contents=[],
                 styles=[]
                 ):
        """
        constructor:

        :param offering_code: URL
        :param operations: List[OwcOperation]
        :param contents: List[OwcContent]
        :param styles: List[OwcStyleSet]
        """
        self.offering_code = offering_code
        self.operations = operations
        self.contents = contents
        self.styles = styles

    def to_dict(self):
        return {
            "code": self.offering_code,
            "operations": [] if len(self.operations) <= 0 else
            [obj.to_dict() for obj in self.operations],
            "contents": [] if len(self.contents) <= 0 else
            [obj.to_dict() for obj in self.contents],
            "styles": [] if len(self.styles) <= 0 else
            [obj.to_dict() for obj in self.styles]
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcOffering(
            offering_code=extract_p('code', d, None),
            operations=[OwcOperation.from_dict(do) for do in
                        extract_p('operations', d, [])],
            contents=[OwcContent.from_dict(do) for do in
                      extract_p('contents', d, [])],
            styles=[OwcStyleSet.from_dict(do) for do in
                    extract_p('styles', d, [])]
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcOperation(object):
    """
    * + code :CharacterString
    * + method :CharacterString
    * + type :CharacterString
    * + requestURL :URI
    * + request :Content [0..1]
    * + result :Any [0..1]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 operations_code,
                 http_method,
                 request_url,
                 mimetype=None,
                 request=None,
                 result=None
                 ):
        """
        constructor:

        :param operations_code: String (e.g. GetCapabilities)
        :param http_method: String, HTTP verb (GET, POST ..)
        :param request_url: URL
        :param mimetype: String, MIME media type of the EXPECTED results
        :param request: Option[OwcContent] = None
        :param result:Option[OwcContent] = None
        """
        self.operations_code = operations_code
        self.http_method = http_method
        self.request_url = request_url
        self.mimetype = mimetype
        self.request = request
        self.result = result

    def to_dict(self):
        return {
            "code": self.operations_code,
            "method": self.http_method,
            "type": self.mimetype,
            "href": self.request_url,
            "request":
                None if self.request is None else self.request.to_dict(),
            "result":
                None if self.result is None else self.result.to_dict()
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcOperation(
            operations_code=extract_p('code', d, None),
            http_method=extract_p('method', d, None),
            mimetype=extract_p('type', d, None),
            request_url=extract_p('href', d, None),
            request=build_from_xp('request', d, OwcContent, None),
            result=build_from_xp('result', d, OwcContent, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcStyleSet(object):
    """
    * + name :CharacterString
    * + title :CharacterString
    * + abstract :CharacterString [0..1]
    * + default :Boolean [0..1]
    * + legendURL :URI [0..*]
    * + content :Content [0..1]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 name,
                 title,
                 subtitle=None,
                 is_default=None,
                 legend_url=None,
                 content=None
                 ):
        """
        constructor:

        :param name: String
        :param title: String
        :param subtitle: String
        :param is_default: Boolean
        :param legend_url: URL
        :param content: Option[OwcContent] = None
        """
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.is_default = is_default
        self.legend_url = legend_url
        self.content = content

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "abstract": self.subtitle,
            "default": self.is_default,
            "legendURL": self.legend_url,
            "content":
                None if self.content is None else self.content.to_dict()
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcStyleSet(
            name=extract_p('name', d, None),
            title=extract_p('title', d, None),
            subtitle=extract_p('abstract', d, None),
            is_default=extract_p('default', d, None),
            legend_url=extract_p('legendURL', d, None),
            content=build_from_xp('content', d, OwcContent, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)


class OwcContent(object):
    """
    * + type :CharacterString
    * + URL :URI [0..1]
    * + content :Any [0..1]
    * + extension :Any [0..*]
    """

    def __init__(self,
                 mimetype,
                 content,
                 url=None,
                 title=None
                 ):
        """
        constructor:

        :param mimetype: String
        :param content: String encoded, actual content/data
        :param url: URL
        :param title: String
        """
        self.mimetype = mimetype
        self.content = content
        self.url = url
        self.title = title

    def to_dict(self):
        return {
            "type": self.mimetype,
            "url": self.url,
            "content": self.content,
            "title": self.title
        }

    def __str__(self):
        return str(self.to_dict())

    def to_json(self):
        return encode_json(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return OwcContent(
            mimetype=extract_p('type', d, None),
            content=extract_p('content', d, None),
            url=extract_p('url', d, None),
            title=extract_p('title', d, None)
        )

    @classmethod
    def from_json(cls, jsondata):
        d = decode_json(jsondata)
        return cls.from_dict(d)
