#!/usr/bin/python
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

namespaces = {
    None : 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/'
}

class DIF(object):
    """ Process DIF """
    def __init__(self, md):
        val = md.find(util.nspath('Entry_ID', namespaces['dif']))
        self.identifier = util.testXMLValue(val)

        val = md.find(util.nspath('Entry_Title', namespaces['dif']))
        self.title = util.testXMLValue(val)

        self.citation = []
        for el in md.findall(util.nspath('Data_Set_Citation', namespaces['dif'])):
            self.citation.append(Citation(el))

        self.personnel = []
        for el in md.findall(util.nspath('Personnel', namespaces['dif'])):
            self.personnel.append(util.testXMLValue(el))

        self.discipline = []
        for el in md.findall(util.nspath('Discipline', namespaces['dif'])):
            self.discipline.append(util.testXMLValue(el))

        self.parameters= []
        for el in md.findall(util.nspath('Parameters', namespaces['dif'])):
            self.parameters.append(util.testXMLValue(el))

        self.iso_topic_category  = []
        for el in md.findall(util.nspath('ISO_Topic_Category', namespaces['dif'])):
            self.iso_topic_category.append(util.testXMLValue(el))

        self.keyword = []
        for el in md.findall(util.nspath('Keyword', namespaces['dif'])):
            self.keyword.append(util.testXMLValue(el))

        self.sensor_name = []
        for el in md.findall(util.nspath('Sensor_Name', namespaces['dif'])):
            self.sensor_name.append(Name(el))

        self.source_name = []
        for el in md.findall(util.nspath('Source_Name', namespaces['dif'])):
            self.source_name.append(Name(el))

        self.temporal_coverage = []
        for el in md.findall(util.nspath('Temporal_Coverage', namespaces['dif'])):
            self.temporal_coverage.append(Temporal_Coverage(el))

        self.paleo_temporal_coverage = []
        for el in md.findall(util.nspath('Paleo_Temporal_Coverage', namespaces['dif'])):
            self.paleo_temporal_coverage.append(Paleo_Temporal_Coverage(el))

        self.data_set_progress = []
        for el in md.findall(util.nspath('Data_Set_Progress', namespaces['dif'])):
            self.data_set_progress.append(util.testXMLValue(el))

        self.spatial_coverage = []
        for el in md.findall(util.nspath('Spatial_Coverage', namespaces['dif'])):
            self.spatial_coverage.append(Spatial_Coverage(el))

        self.location = []
        for el in md.findall(util.nspath('location', namespaces['dif'])):
            self.location.append(util.testXMLValue(el))

        self.data_resolution = []
        for el in md.findall(util.nspath('Data_Resolution', namespaces['dif'])):
            self.data_resolution.append(Data_Resolution(el))

        self.project = []
        for el in md.findall(util.nspath('Project', namespaces['dif'])):
            self.project.append(Name(el))

        val = md.find(util.nspath('Quality', namespaces['dif']))
        self.quality = util.testXMLValue(val)

        val = md.find(util.nspath('Access_Constraints', namespaces['dif']))
        self.access_constraints = util.testXMLValue(val)

        val = md.find(util.nspath('Use_Constraints', namespaces['dif']))
        self.use_constraints = util.testXMLValue(val)

        self.language = []
        for el in md.findall(util.nspath('Data_Set_Language', namespaces['dif'])):
            self.language.append(util.testXMLValue(el))

        self.originating_center = []
        for el in md.findall(util.nspath('Originating_Center', namespaces['dif'])):
            self.originating_center.append(util.testXMLValue(el))

        self.data_center = []
        for el in md.findall(util.nspath('Data_Center', namespaces['dif'])):         
            self.data_center.append(Data_Center(el))

        self.distribution = []
        for el in md.findall(util.nspath('Distribution', namespaces['dif'])):     
            self.distribution.append(Distribution(el))

        self.multimedia_sample = []
        for el in md.findall(util.nspath('Multimedia_Sample', namespaces['dif'])):     
            self.multimedia_sample.append(Multimedia_Sample(el))

        val = md.find(util.nspath('Reference', namespaces['dif']))
        self.reference = util.testXMLValue(val)

        val = md.find(util.nspath('Summary', namespaces['dif']))
        self.summary = util.testXMLValue(val)

        self.related_url = []
        for el in md.findall(util.nspath('Related_URL', namespaces['dif'])):
            self.related_url.append(Related_URL(el))

        self.parent_dif = []
        for el in md.findall(util.nspath('Parent_DIF', namespaces['dif'])):
            self.parent_dif.append(util.testXMLValue(el))

        self.idn_node = []
        for el in md.findall(util.nspath('IDN_Node', namespaces['dif'])):
            self.idn_node.append(Name(el))

        val = md.find(util.nspath('Originating_Metadata_Node', namespaces['dif']))
        self.originating_metadata_node = util.testXMLValue(val)

        val = md.find(util.nspath('Metadata_Name', namespaces['dif']))
        self.metadata_name = util.testXMLValue(val)

        val = md.find(util.nspath('Metadata_Version', namespaces['dif']))
        self.metadata_version = util.testXMLValue(val)

        val = md.find(util.nspath('DIF_Creation_Date', namespaces['dif']))
        self.dif_creation_date = util.testXMLValue(val)

        val = md.find(util.nspath('Last_DIF_Revision_Date', namespaces['dif']))
        self.last_dif_revision_date = util.testXMLValue(val)

        val = md.find(util.nspath('Future_DIF_Review_Date', namespaces['dif']))
        self.future_dif_review_date = util.testXMLValue(val)

        val = md.find(util.nspath('Private', namespaces['dif']))
        self.private = util.testXMLValue(val)

class Citation(object):
    """ Parse Data_Set_Citation """
    def __init__(self, el):
        val = el.find(util.nspath('Dataset_Creator', namespaces['dif']))
        self.creator = util.testXMLValue(val)

        val = el.find(util.nspath('Dataset_Title', namespaces['dif']))
        self.title = util.testXMLValue(val)

        val = el.find(util.nspath('Dataset_Series_Name', namespaces['dif']))
        self.series_name = util.testXMLValue(val)

        val = el.find(util.nspath('Dataset_Release_Date', namespaces['dif']))
        self.release_date = util.testXMLValue(val)

        val = el.find(util.nspath('Dataset_Release_Place', namespaces['dif']))
        self.release_place = util.testXMLValue(val)

        val = el.find(util.nspath('Dataset_Publisher', namespaces['dif']))
        self.publisher = util.testXMLValue(val)

        val = el.find(util.nspath('Version', namespaces['dif']))
        self.version = util.testXMLValue(val)

        val = el.find(util.nspath('Issue_Identification', namespaces['dif']))
        self.issue_identification = util.testXMLValue(val)

        val = el.find(util.nspath('Data_Presentation_Form', namespaces['dif']))
        self.presentation_form = util.testXMLValue(val)

        val = el.find(util.nspath('Other_Citation_Details', namespaces['dif']))
        self.details = util.testXMLValue(val)

        val = el.find(util.nspath('Online_Resource', namespaces['dif']))
        self.onlineresource = util.testXMLValue(val)

class Personnel(object):
    """ Process Personnel """
    def __init__(self, md):
        self.role = []
        for el in md.findall(util.nspath('Role', namespaces['dif'])):
            self.role.append(util.testXMLValue(el))

        val = md.find(util.nspath('First_Name', namespaces['dif']))
        self.first_name = util.testXMLValue(val)

        val = md.find(util.nspath('Middle_Name', namespaces['dif']))
        self.middle_name = util.testXMLValue(val)

        val = md.find(util.nspath('Last_Name', namespaces['dif']))
        self.last_name = util.testXMLValue(val)

        self.email = []
        for el in md.findall(util.nspath('Email', namespaces['dif'])):
            self.email.append(util.testXMLValue(el))

        self.phone = []
        for el in md.findall(util.nspath('Phone', namespaces['dif'])):
            self.phone.append(util.testXMLValue(el))

        self.fax = []
        for el in md.findall(util.nspath('Fax', namespaces['dif'])):
            self.fax.append(util.testXMLValue(el))

        val = md.find(util.nspath('Contact_Address', namespaces['dif']))
        self.contact_address = Contact_Address(val)

class Contact_Address(object):
    """ Process Contact_Address """
    def __init__(self, md):
        self.address = []
        for el in md.findall(util.nspath('Address', namespaces['dif'])):
            self.address.append(util.testXMLValue(el))

        val = md.find(util.nspath('City', namespaces['dif']))
        self.city = util.testXMLValue(val)

        val = md.find(util.nspath('Province_or_State', namespaces['dif']))
        self.province_or_state = util.testXMLValue(val)

        val = md.find(util.nspath('Postal_Code', namespaces['dif']))
        self.postal_code = util.testXMLValue(val)

        val = md.find(util.nspath('Country', namespaces['dif']))
        self.country = util.testXMLValue(val)

class Discipline(object):
    """ Process Discipline """
    def __init__(self, md):
        val = md.find(util.nspath('Discipline_Name', namespaces['dif']))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath('Subdiscipline', namespaces['dif']))
        self.subdiscipline = util.testXMLValue(val)

        val = md.find(util.nspath('Detailed_Subdiscipline', namespaces['dif']))
        self.detailed_subdiscipline = util.testXMLValue(val)

class Parameters(object):
    """ Process Parameters """
    def __init__(self, md):
        val = md.find(util.nspath('Category', namespaces['dif']))
        self.category = util.testXMLValue(val)

        val = md.find(util.nspath('Topic', namespaces['dif']))
        self.topic = util.testXMLValue(val)

        val = md.find(util.nspath('Term', namespaces['dif']))
        self.term = util.testXMLValue(val)

        val = md.find(util.nspath('Variable_Level_1', namespaces['dif']))
        self.variable_l1 = util.testXMLValue(val)

        val = md.find(util.nspath('Variable_Level_2', namespaces['dif']))
        self.variable_l2 = util.testXMLValue(val)
    
        val = md.find(util.nspath('Variable_Level_3', namespaces['dif']))
        self.variable_l3 = util.testXMLValue(val)
 
        val = md.find(util.nspath('Detailed_Variable', namespaces['dif']))
        self.detailed_variable = util.testXMLValue(val)

class Name(object):
    """ Process Sensor_Name, Source_Name, Project, IDN_Node """
    def __init__(self, md):
        val = md.find(util.nspath('Short_Name', namespaces['dif']))
        self.short_name = util.testXMLValue(val)

        val = md.find(util.nspath('Long_Name', namespaces['dif']))
        self.long_name = util.testXMLValue(val)

class Temporal_Coverage(object):
    """ Process Temporal_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath('Start_Date', namespaces['dif']))
        self.start_date = util.testXMLValue(val)
        
        val = md.find(util.nspath('End_Date', namespaces['dif']))
        self.end_date = util.testXMLValue(val)

class Paleo_Temporal_Coverage(object):
    """ Process Paleo_Temporal_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath('Paleo_Start_Date', namespaces['dif']))
        self.paleo_start_date = util.testXMLValue(val)

        val = md.find(util.nspath('Paleo_End_Date', namespaces['dif']))
        self.paleo_end_date = util.testXMLValue(val)

        self.chronostratigraphic_unit = []
        for el in md.findall(util.nspath('Chronostratigraphic_Unit', namespaces['dif'])):
            self.chronostratigraphic_unit.append(Chronostratigraphic_Unit(el))

class Chronostratigraphic_Unit(object):
    """ Process Chronostratigraphic_Unit """
    def __init__(self, md):
        val = md.find(util.nspath('Eon', namespaces['dif']))
        self.eon = util.testXMLValue(val)

        val = md.find(util.nspath('Era', namespaces['dif']))
        self.era = util.testXMLValue(val)

        val = md.find(util.nspath('Period', namespaces['dif']))
        self.period = util.testXMLValue(val)

        val = md.find(util.nspath('Epoch', namespaces['dif']))
        self.epoch = util.testXMLValue(val)

        val = md.find(util.nspath('Stage', namespaces['dif']))
        self.stage = util.testXMLValue(val)

        val = md.find(util.nspath('Detailed_Classification', namespaces['dif']))
        self.detailed_classification = util.testXMLValue(val)

class Spatial_Coverage(object):
    """ Process Spatial_Coverage """
    def __init__(self, md):
        val = md.find(util.nspath('Southernmost_Latitude', namespaces['dif']))
        self.miny = util.testXMLValue(val)

        val = md.find(util.nspath('Northernmost_Latitude', namespaces['dif']))
        self.maxy = util.testXMLValue(val)

        val = md.find(util.nspath('Westernmost_Latitude', namespaces['dif']))
        self.minx = util.testXMLValue(val)

        val = md.find(util.nspath('Easternmost_Latitude', namespaces['dif']))
        self.maxx = util.testXMLValue(val)

        val = md.find(util.nspath('Minimum_Altitude', namespaces['dif']))
        self.minz = util.testXMLValue(val)

        val = md.find(util.nspath('Maximum_Altitude', namespaces['dif']))
        self.maxz = util.testXMLValue(val)

        val = md.find(util.nspath('Minimum_Depth', namespaces['dif']))
        self.mindepth = util.testXMLValue(val)

        val = md.find(util.nspath('Maximum_Depth', namespaces['dif']))
        self.maxdepth = util.testXMLValue(val)

class Location(object):
    """ Process Location """
    def __init__(self, md):
        val = md.find(util.nspath('Location_Category', namespaces['dif']))
        self.category = util.testXMLValue(val)

        val = md.find(util.nspath('Location_Category', namespaces['dif']))
        self.type = util.testXMLValue(val)

        val = md.find(util.nspath('Location_Subregion1', namespaces['dif']))
        self.subregion1 = util.testXMLValue(val)

        val = md.find(util.nspath('Location_Subregion2', namespaces['dif']))
        self.subregion2 = util.testXMLValue(val)

        val = md.find(util.nspath('Location_Subregion3', namespaces['dif']))
        self.subregion3 = util.testXMLValue(val)

        val = md.find(util.nspath('Detailed_Location', namespaces['dif']))
        self.detailed_location = util.testXMLValue(val)

class Data_Resolution(object):
    """ Process Data_Resolution"""
    def __init__(self, md):
        val = md.find(util.nspath('Latitude_Resolution', namespaces['dif']))
        self.y = util.testXMLValue(val)

        val = md.find(util.nspath('Longitude_Resolution', namespaces['dif']))
        self.x = util.testXMLValue(val)

        val = md.find(util.nspath('Horizontal_Resolution_Range', namespaces['dif']))
        self.horizontal_res_range = util.testXMLValue(val)

        val = md.find(util.nspath('Vertical_Resolution', namespaces['dif']))
        self.vertical_res = util.testXMLValue(val)

        val = md.find(util.nspath('Vertical_Resolution_Range', namespaces['dif']))
        self.vertical_res_range = util.testXMLValue(val)

        val = md.find(util.nspath('Temporal_Resolution', namespaces['dif']))
        self.temporal_res = util.testXMLValue(val)

        val = md.find(util.nspath('Temporal_Resolution_Range', namespaces['dif']))
        self.temporal_res_range = util.testXMLValue(val)

class Data_Center(object):
    """ Process Data_Center """
    def __init__(self, md):
        val = md.find(util.nspath('Data_Center_Name', namespaces['dif']))
        self.name = util.testXMLValue(val)

        val = md.find(util.nspath('Data_Center_URL', namespaces['dif']))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath('Data_Set_ID', namespaces['dif']))
        self.data_set_id = util.testXMLValue(val)

        val = md.find(util.nspath('Personnel', namespaces['dif']))
        self.personnel = util.testXMLValue(val)

class Distribution(object):
    """ Process Distribution """
    def __init__(self, md):
        val = md.find(util.nspath('Distribution_Media', namespaces['dif']))
        self.media = util.testXMLValue(val)

        val = md.find(util.nspath('Distribution_Size', namespaces['dif']))
        self.size = util.testXMLValue(val)

        val = md.find(util.nspath('Distribution_Format', namespaces['dif']))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath('Fees', namespaces['dif']))
        self.fees = util.testXMLValue(val)

class Multimedia_Sample(object):
    """ Process Multimedia_Sample """
    def __init__(self, md):
        val = md.find(util.nspath('File', namespaces['dif']))
        self.file = util.testXMLValue(val)

        val = md.find(util.nspath('URL', namespaces['dif']))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath('Format', namespaces['dif']))
        self.format = util.testXMLValue(val)

        val = md.find(util.nspath('Caption', namespaces['dif']))
        self.caption = util.testXMLValue(val)

        val = md.find(util.nspath('Description', namespaces['dif']))
        self.description = util.testXMLValue(val)

        val = md.find(util.nspath('Visualization_URL', namespaces['dif']))
        self.vis_url = util.testXMLValue(val)

        val = md.find(util.nspath('Visualization_Type', namespaces['dif']))
        self.vis_type = util.testXMLValue(val)

        val = md.find(util.nspath('Visualization_Subtype', namespaces['dif']))
        self.vis_subtype = util.testXMLValue(val)

        val = md.find(util.nspath('Visualization_Duration', namespaces['dif']))
        self.vis_duration = util.testXMLValue(val)

        val = md.find(util.nspath('Visualization_File_Size', namespaces['dif']))
        self.file_size = util.testXMLValue(val)

class Related_URL(object):
    """ Process Related_URL """
    def __init__(self, md):
        self.content_type = []
        for el in md.findall(util.nspath('URL_Content_Type', namespaces['dif'])):
            self.content_type.append(URL_Content_Type(el))

        val = md.find(util.nspath('URL', namespaces['dif']))
        self.url = util.testXMLValue(val)

        val = md.find(util.nspath('Description', namespaces['dif']))
        self.description = util.testXMLValue(val)

class URL_Content_Type(object):
    """ Process URL_Content_Type """
    def __init__(self, md):
        val = md.find(util.nspath('Type', namespaces['dif']))
        self.type = util.testXMLValue(val)

        val = md.find(util.nspath('SubType', namespaces['dif']))
        self.subtype = util.testXMLValue(val)











