# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2009 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

""" DIF metadata parser """

from owslib.etree import etree
from owslib import util

# default variables

class DIF(object):
    """ Process DIF """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Entry_ID'))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Entry_Title'))
        self.title = util.testXMLValue(val)

        self.citation = []
        for el in md.findall(util.nspath_eval('dif:Data_Set_Citation')):
            self.citation.append(Citation(el))

        self.personnel = []
        for el in md.findall(util.nspath_eval('dif:Personnel')):
            self.personnel.append(util.testXMLValue(el))

        self.discipline = []
        for el in md.findall(util.nspath_eval('dif:Discipline')):
            self.discipline.append(util.testXMLValue(el))

        self.parameters= []
        for el in md.findall(util.nspath_eval('dif:Parameters')):
            self.parameters.append(util.testXMLValue(el))

        self.iso_topic_category  = []
        for el in md.findall(util.nspath_eval('dif:ISO_Topic_Category')):
            self.iso_topic_category.append(util.testXMLValue(el))

        self.keyword = []
        for el in md.findall(util.nspath_eval('dif:Keyword')):
            self.keyword.append(util.testXMLValue(el))

        self.sensor_name = []
        for el in md.findall(util.nspath_eval('dif:Sensor_Name')):
            self.sensor_name.append(Name(el))

        self.source_name = []
        for el in md.findall(util.nspath_eval('dif:Source_Name')):
            self.source_name.append(Name(el))

        self.temporal_coverage = []
        for el in md.findall(util.nspath_eval('dif:Temporal_Coverage')):
            self.temporal_coverage.append(Temporal_Coverage(el))

        self.paleo_temporal_coverage = []
        for el in md.findall(util.nspath_eval('dif:Paleo_Temporal_Coverage')):
            self.paleo_temporal_coverage.append(Paleo_Temporal_Coverage(el))

        self.data_set_progress = []
        for el in md.findall(util.nspath_eval('dif:Data_Set_Progress')):
            self.data_set_progress.append(util.testXMLValue(el))

        self.spatial_coverage = []
        for el in md.findall(util.nspath_eval('dif:Spatial_Coverage')):
            self.spatial_coverage.append(Spatial_Coverage(el))

        self.location = []
        for el in md.findall(util.nspath_eval('dif:location')):
            self.location.append(util.testXMLValue(el))

        self.data_resolution = []
        for el in md.findall(util.nspath_eval('dif:Data_Resolution')):
            self.data_resolution.append(Data_Resolution(el))

        self.project = []
        for el in md.findall(util.nspath_eval('dif:Project')):
            self.project.append(Name(el))

        val = md.find(util.nspath_eval('dif:Quality'))
        self.quality = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Access_Constraints'))
        self.access_constraints = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Use_Constraints'))
        self.use_constraints = util.testXMLValue(val)

        self.language = []
        for el in md.findall(util.nspath_eval('dif:Data_Set_Language')):
            self.language.append(util.testXMLValue(el))

        self.originating_center = []
        for el in md.findall(util.nspath_eval('dif:Originating_Center')):
            self.originating_center.append(util.testXMLValue(el))

        self.data_center = []
        for el in md.findall(util.nspath_eval('dif:Data_Center')):         
            self.data_center.append(Data_Center(el))

        self.distribution = []
        for el in md.findall(util.nspath_eval('dif:Distribution')):     
            self.distribution.append(Distribution(el))

        self.multimedia_sample = []
        for el in md.findall(util.nspath_eval('dif:Multimedia_Sample')):     
            self.multimedia_sample.append(Multimedia_Sample(el))

        val = md.find(util.nspath_eval('dif:Reference'))
        self.reference = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Summary'))
        self.summary = util.testXMLValue(val)

        self.related_url = []
        for el in md.findall(util.nspath_eval('dif:Related_URL')):
            self.related_url.append(Related_URL(el))

        self.parent_dif = []
        for el in md.findall(util.nspath_eval('dif:Parent_DIF')):
            self.parent_dif.append(util.testXMLValue(el))

        self.idn_node = []
        for el in md.findall(util.nspath_eval('dif:IDN_Node')):
            self.idn_node.append(Name(el))

        val = md.find(util.nspath_eval('dif:Originating_Metadata_Node'))
        self.originating_metadata_node = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Metadata_Name'))
        self.metadata_name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Metadata_Version'))
        self.metadata_version = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:DIF_Creation_Date'))
        self.dif_creation_date = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Last_DIF_Revision_Date'))
        self.last_dif_revision_date = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Future_DIF_Review_Date'))
        self.future_dif_review_date = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Private'))
        self.private = util.testXMLValue(val)

class Citation(object):
    """ Parse Data_Set_Citation """
    def __init__(self, el):
        val = el.find(util.nspath_eval('dif:Dataset_Creator'))
        self.creator = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Dataset_Title'))
        self.title = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Dataset_Series_Name'))
        self.series_name = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Dataset_Release_Date'))
        self.release_date = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Dataset_Release_Place'))
        self.release_place = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Dataset_Publisher'))
        self.publisher = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Version'))
        self.version = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Issue_Identification'))
        self.issue_identification = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Data_Presentation_Form'))
        self.presentation_form = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Other_Citation_Details'))
        self.details = util.testXMLValue(val)

        val = el.find(util.nspath_eval('dif:Online_Resource'))
        self.onlineresource = util.testXMLValue(val)

class Personnel(object):
    """ Process Personnel """
    def __init__(self, md):
        self.role = []
        for el in md.findall(util.nspath_eval('dif:Role')):
            self.role.append(util.testXMLValue(el))

        val = md.find(util.nspath_eval('dif:First_Name'))
        self.first_name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Middle_Name'))
        self.middle_name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Last_Name'))
        self.last_name = util.testXMLValue(val)

        self.email = []
        for el in md.findall(util.nspath_eval('dif:Email')):
            self.email.append(util.testXMLValue(el))

        self.phone = []
        for el in md.findall(util.nspath_eval('dif:Phone')):
            self.phone.append(util.testXMLValue(el))

        self.fax = []
        for el in md.findall(util.nspath_eval('dif:Fax')):
            self.fax.append(util.testXMLValue(el))

        val = md.find(util.nspath_eval('dif:Contact_Address'))
        self.contact_address = Contact_Address(val)

class Contact_Address(object):
    """ Process Contact_Address """
    def __init__(self, md):
        self.address = []
        for el in md.findall(util.nspath_eval('dif:Address')):
            self.address.append(util.testXMLValue(el))

        val = md.find(util.nspath_eval('dif:City'))
        self.city = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Province_or_State'))
        self.province_or_state = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Postal_Code'))
        self.postal_code = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Country'))
        self.country = util.testXMLValue(val)

class Discipline(object):
    """ Process Discipline """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Discipline_Name'))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Subdiscipline'))
        self.subdiscipline = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Detailed_Subdiscipline'))
        self.detailed_subdiscipline = util.testXMLValue(val)

class Parameters(object):
    """ Process Parameters """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Category'))
        self.category = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Topic'))
        self.topic = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Term'))
        self.term = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Variable_Level_1'))
        self.variable_l1 = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Variable_Level_2'))
        self.variable_l2 = util.testXMLValue(val)
    
        val = md.find(util.nspath_eval('dif:Variable_Level_3'))
        self.variable_l3 = util.testXMLValue(val)
 
        val = md.find(util.nspath_eval('dif:Detailed_Variable'))
        self.detailed_variable = util.testXMLValue(val)

class Name(object):
    """ Process Sensor_Name, Source_Name, Project, IDN_Node """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Short_Name'))
        self.short_name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Long_Name'))
        self.long_name = util.testXMLValue(val)

class Temporal_Coverage(object):
    """ Process Temporal_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Start_Date'))
        self.start_date = util.testXMLValue(val)
        
        val = md.find(util.nspath_eval('dif:End_Date'))
        self.end_date = util.testXMLValue(val)

class Paleo_Temporal_Coverage(object):
    """ Process Paleo_Temporal_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Paleo_Start_Date'))
        self.paleo_start_date = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Paleo_End_Date'))
        self.paleo_end_date = util.testXMLValue(val)

        self.chronostratigraphic_unit = []
        for el in md.findall(util.nspath_eval('dif:Chronostratigraphic_Unit')):
            self.chronostratigraphic_unit.append(Chronostratigraphic_Unit(el))

class Chronostratigraphic_Unit(object):
    """ Process Chronostratigraphic_Unit """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Eon'))
        self.eon = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Era'))
        self.era = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Period'))
        self.period = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Epoch'))
        self.epoch = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Stage'))
        self.stage = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Detailed_Classification'))
        self.detailed_classification = util.testXMLValue(val)

class Spatial_Coverage(object):
    """ Process Spatial_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Southernmost_Latitude'))
        self.miny = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Northernmost_Latitude'))
        self.maxy = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Westernmost_Latitude'))
        self.minx = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Easternmost_Latitude'))
        self.maxx = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Minimum_Altitude'))
        self.minz = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Maximum_Altitude'))
        self.maxz = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Minimum_Depth'))
        self.mindepth = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Maximum_Depth'))
        self.maxdepth = util.testXMLValue(val)

class Location(object):
    """ Process Location """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Location_Category'))
        self.category = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Location_Category'))
        self.type = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Location_Subregion1'))
        self.subregion1 = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Location_Subregion2'))
        self.subregion2 = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Location_Subregion3'))
        self.subregion3 = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Detailed_Location'))
        self.detailed_location = util.testXMLValue(val)

class Data_Resolution(object):
    """ Process Data_Resolution"""
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Latitude_Resolution'))
        self.y = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Longitude_Resolution'))
        self.x = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Horizontal_Resolution_Range'))
        self.horizontal_res_range = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Vertical_Resolution'))
        self.vertical_res = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Vertical_Resolution_Range'))
        self.vertical_res_range = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Temporal_Resolution'))
        self.temporal_res = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Temporal_Resolution_Range'))
        self.temporal_res_range = util.testXMLValue(val)

class Data_Center(object):
    """ Process Data_Center """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Data_Center_Name'))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Data_Center_URL'))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Data_Set_ID'))
        self.data_set_id = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Personnel'))
        self.personnel = util.testXMLValue(val)

class Distribution(object):
    """ Process Distribution """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Distribution_Media'))
        self.media = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Distribution_Size'))
        self.size = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Distribution_Format'))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Fees'))
        self.fees = util.testXMLValue(val)

class Multimedia_Sample(object):
    """ Process Multimedia_Sample """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:File'))
        self.file = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:URL'))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Format'))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Caption'))
        self.caption = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Description'))
        self.description = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Visualization_URL'))
        self.vis_url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Visualization_Type'))
        self.vis_type = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Visualization_Subtype'))
        self.vis_subtype = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Visualization_Duration'))
        self.vis_duration = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Visualization_File_Size'))
        self.file_size = util.testXMLValue(val)

class Related_URL(object):
    """ Process Related_URL """
    def __init__(self, md):
        self.content_type = []
        for el in md.findall(util.nspath_eval('dif:URL_Content_Type')):
            self.content_type.append(URL_Content_Type(el))

        val = md.find(util.nspath_eval('dif:URL'))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:Description'))
        self.description = util.testXMLValue(val)

class URL_Content_Type(object):
    """ Process URL_Content_Type """
    def __init__(self, md):
        val = md.find(util.nspath_eval('dif:Type'))
        self.type = util.testXMLValue(val)

        val = md.find(util.nspath_eval('dif:SubType'))
        self.subtype = util.testXMLValue(val)











