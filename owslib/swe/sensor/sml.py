# encoding: utf-8

from owslib.etree import etree
from owslib import crs, util
from owslib.util import testXMLValue, nspath_eval, xmltag_split, dict_union, extract_xml_list
from owslib.namespaces import Namespaces

def get_namespaces():
    n = Namespaces()
    return n.get_namespaces(["sml","gml","xlink"])
namespaces = get_namespaces()

class SensorML(object):
    def __init__(self, element):
        if isinstance(element, str):
            self._root = etree.fromstring(element)
        else:
            self._root = element

        if hasattr(self._root, 'getroot'):
            self._root = self._root.getroot()

        self.systems = []
        for system in self._root.findall(nspath_eval('sml:member/sml:System', namespaces)):
            self.systems.append(SystemMetadata(system))

class SystemMetadata(object):
    """
    <sml:System gml:id="station-52402">
        <gml:description>...</gml:description>
        <sml:keywords>...</sml:keywords>
        <sml:identification>...</sml:identification>
        <sml:classification>...</sml:classification>
        <sml:validTime>...</sml:validTime>
        <sml:timePosition>...</sml:timePosition>
        <sml:contact xlink:role="urn:ogc:def:classifiers:OGC:contactType:owner">...</sml:contact>
        <sml:documentation xlink:arcrole="urn:ogc:def:role:webPage">...</sml:documentation>
        <sml:documentation xlink:arcrole="urn:ogc:def:role:objectImage">...</sml:documentation>
        <sml:history>...</sml:history>
        <sml:components>...</sml:components>
        <sml:positions>...</sml:positions>
        <sml:position>...</sml:position>
        <sml:location>...</sml:location>
    </sml:System>
    """
    def __init__(self, element):
        self._root = element

        self.id = testXMLValue(self._root.attrib.get(nspath_eval('gml:id', namespaces)), True)
        self.description = testXMLValue(self._root.find(nspath_eval('gml:description', namespaces)))
        self.keywords = extract_xml_list(self._root.findall(nspath_eval('sml:keywords/sml:KeywordList/sml:keyword', namespaces)))

        self.documents = []
        for document in self._root.findall(nspath_eval('sml:documentation', namespaces)):
            self.documents.append(DocumentationMetadata(document))

        self.identifiers = {}
        for identifier in self._root.findall(nspath_eval('sml:identification/sml:IdentifierList/sml:identifier', namespaces)):
            ident = IdentifierMetadata(identifier)
            self.identifiers[ident.name] = ident

        self.contacts = {}
        for contact in self._root.findall(nspath_eval('sml:contact', namespaces)):
            cont = ContactMetadata(contact)
            self.contacts[cont.role] = cont

        self.classifiers = {}
        for classifier in self._root.findall(nspath_eval('sml:classification/sml:ClassifierList/sml:classifier', namespaces)):
            classi = ClassifierMetadata(classifier)
            self.classifiers[classi.name] = classi

        self.history = {}
        for event_member in self._root.findall(nspath_eval('sml:history/sml:EventList/sml:member', namespaces)):
            emm = EventMemberMetadata(event_member)
            if self.history.get(emm.name) is None:
                self.history[emm.name] = []
            self.history[emm.name] += emm.events
    
        self.components = {}

        #TODO: Components, timePosition, validTime, positiion/location/positions, 

    def get_identifier_by_name(self, name):
        """
            Return a IdentifierMetadata by name, case insensitive
        """
        for identifier in self.identifiers.keys():
            if identifier.lower() == name.lower():
                return self.identifiers[identifier]
        raise KeyError, "No Identifier with name: %s" % name

    def get_contact_by_role(self, role):
        """
            Return a ContactMetadata by role, case insensitive
        """
        for contact in self.contacts.keys():
            if contact.lower() == role.lower():
                return self.contacts[contact]
        raise KeyError, "No Contasct with role: %s" % role

    def get_classifier_by_name(self, name):
        """
            Return a ClassifierMetadata by name, case insensitive
        """
        for classi in self.classifiers.keys():
            if classi.lower() == name.lower():
                return self.classifiers[classi]
        raise KeyError, "No Classifier with name: %s" % name

    def get_history_by_name(self, name):
        """
            Return a EventMemberMetadata by name, case insensitive
        """
        for his in self.history.keys():
            if his.lower() == name.lower():
                return self.history[his]
        raise KeyError, "No Classifier with name: %s" % name


class EventMemberMetadata(object):
    """
    <sml:member name="deployment_start">
        <sml:Event>
            <sml:date>2010-01-12</sml:date>
            <gml:description>Deployment start event</gml:description>
            <sml:documentation xlink:href="http://sdftest.ndbc.noaa.gov/sos/server.php?service=SOS&request=DescribeSensor&version=1.0.0&outputformat=text/xml;subtype="sensorML/1.0.1"&procedure=urn:ioos:station:wmo:48900:20100112"/>
        </sml:Event>
        <sml:Event>
            <sml:date>2010-01-13</sml:date>
            <gml:description>Deployment end event</gml:description>
            <sml:documentation xlink:href="http://sdftest.ndbc.noaa.gov/sos/server.php?service=SOS&request=DescribeSensor&version=1.0.0&outputformat=text/xml;subtype="sensorML/1.0.1"&procedure=urn:ioos:station:wmo:48900:20100113"/>
        </sml:Event>
    </sml:member>
    """
    def __init__(self, element):
        self._root = element

        self.name = testXMLValue(self._root.attrib.get('name'), True)

        self.events = []
        for event in self._root.findall(nspath_eval('sml:Event', namespaces)):
            self.events.append(EventMetadata(event, self.name))

class EventMetadata(object):
    """
    <sml:Event>
        <sml:date>2010-01-12</sml:date>
        <gml:description>Deployment start event</gml:description>
        <sml:documentation xlink:href="http://sdftest.ndbc.noaa.gov/sos/server.php?service=SOS&request=DescribeSensor&version=1.0.0&outputformat=text/xml;subtype="sensorML/1.0.1"&procedure=urn:ioos:station:wmo:48900:20100112"/>
    </sml:Event>
    """
    def __init__(self, element, name):
        self._root = element

        self.name = name
        # All dates are UTC
        self.date = testXMLValue(self._root.find(nspath_eval('sml:date', namespaces)))
        self.description = testXMLValue(self._root.find(nspath_eval('gml:description', namespaces)))
        documentation = self._root.find(nspath_eval('sml:documentation', namespaces))
        if documentation is not None:
            self.documentation_url = testXMLValue(documentation.attrib.get(nspath_eval('xlink:href', namespaces)), True)
        else:
            self.documentation_url = None

class ClassifierMetadata(object):
    """
    <sml:classifier name="Parent Network">
        <sml:Term definition="urn-:x-noaa:def:classifier:NOAA::parentNetwork">
            <sml:codeSpace xlink:href="http://sdf.ndbc.noaa.gov"/>
            <sml:value>
                urn:x-noaa:def:network:noaa.nws.ndbc::TsunamiActive
            </sml:value>
        </sml:Term>
    </sml:classifier>
    """
    def __init__(self, element):
        self._root = element
        self.name = testXMLValue(self._root.attrib.get('name'), True)
        self.definition = testXMLValue(self._root.find(nspath_eval('sml:Term', namespaces)).attrib.get('definition'), True)
        self.codespace = testXMLValue(self._root.find(nspath_eval('sml:Term/sml:codeSpace', namespaces)).attrib.get(nspath_eval('xlink:href', namespaces)), True)
        self.value = testXMLValue(self._root.find(nspath_eval('sml:Term/sml:value', namespaces)))

class DocumentationMetadata(object):
    """
    <sml:documentation xlink:arcrole="qualityControlDocument">
        <sml:Document>
            <gml:description>
                Handbook of Automated Data Quality Control Checks and Procedures, National Data Buoy Center, August 2009
            </gml:description>
            <sml:format>pdf</sml:format>
            <sml:onlineResource xlink:href="http://www.ndbc.noaa.gov/NDBCHandbookofAutomatedDataQualityControl2009.pdf"/>
        </sml:Document>
    </sml:documentation>
    """
    def __init__(self, element):
        self._root = element
        self.arcrole = testXMLValue(self._root.attrib.get(nspath_eval('xlink:arcrole', namespaces)), True)
        self.description = testXMLValue(self._root.find(nspath_eval('sml:Document/gml:description', namespaces)))
        self.format = testXMLValue(self._root.find(nspath_eval('sml:Document/sml:format', namespaces)))
        self.url = testXMLValue(self._root.find(nspath_eval('sml:Document/sml:onlineResource', namespaces)).attrib.get(nspath_eval('xlink:href', namespaces)), True)

class IdentifierMetadata(object):
    """
    <sml:identifier name="Short Name">
        <sml:Term definition="urn:ogc:def:identifier:OGC:shortName">
            <sml:codeSpace xlink:href="http://sdf.ndbc.noaa.gov"/>
            <sml:value>adcp0</sml:value>
        </sml:Term>
    </sml:identifier>
    """
    def __init__(self, element):
        self._root = element
        self.name = testXMLValue(self._root.attrib.get('name'), True)

        term = self._root.find(nspath_eval('sml:Term', namespaces))
        self.definition = testXMLValue(term.attrib.get('definition'), True)

        val = term.find(nspath_eval('sml:codeSpace', namespaces))
        if val is not None:
            self.codespace = testXMLValue(val.attrib.get(nspath_eval('xlink:href', namespaces)), True)

        self.value = testXMLValue(self._root.find(nspath_eval('sml:Term/sml:value', namespaces)))

class ContactMetadata(object):
    """
    <sml:contact xlink:role="urn:ogc:def:classifiers:OGC:contactType:publisher" xlink:href="http://sdf.ndbc.noaa.gov/">
        <sml:ResponsibleParty>
            <sml:organizationName>National Data Buoy Center</sml:organizationName>
            <sml:contactInfo>
                <sml:phone>
                    <sml:voice>228-688-2805</sml:voice>
                </sml:phone>
                <sml:address>
                    <sml:deliveryPoint>Bldg. 3205</sml:deliveryPoint>
                    <sml:city>Stennis Space Center</sml:city>
                    <sml:administrativeArea>MS</sml:administrativeArea>
                    <sml:postalCode>39529</sml:postalCode>
                    <sml:country>USA</sml:country>
                    <sml:electronicMailAddress>webmaster.ndbc@noaa.gov</sml:electronicMailAddress>
                </sml:address>
            </sml:contactInfo>
        </sml:ResponsibleParty>
    </sml:contact>
    """
    def __init__(self, element):
        self._root = element
        
        self.role = testXMLValue(self._root.attrib.get(nspath_eval('xlink:role', namespaces)), True)
        self.url = testXMLValue(self._root.attrib.get(nspath_eval('xlink:href', namespaces)), True)
        self.organization = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:organizationName', namespaces)))
        self.phone = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:phone/sml:voice', namespaces)))
        self.address = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:deliveryPoint', namespaces)))
        self.city = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:city', namespaces)))
        self.region = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:administrativeArea', namespaces)))
        self.postcode = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:postalCode', namespaces)))
        self.country = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:country', namespaces)))
        self.email = testXMLValue(self._root.find(nspath_eval('sml:ResponsibleParty/sml:contactInfo/sml:address/sml:electronicMailAddress', namespaces)))

        """
        For reference, here is the OWS contact element (ows:ServiceContact)

        self.name = testXMLValue(self._root.find(ns_ows('ows:IndividualName')))
        self.role = testXMLValue(self._root.find(ns_ows('ows:Role')))
        self.position = testXMLValue(self._root.find(ns_ows('ows:PositionName')))
        self.email = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:ElectronicMailAddress')))
        self.address = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:DeliveryPoint')))
        self.city = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:City')))
        self.region = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:AdministrativeArea')))
        self.postcode = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:PostalCode')))
        self.country = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:Country')))
        self.city = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Address/ows:City')))
        self.phone = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Phone/ows:Voice')))
        self.fax = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:Phone/ows:Facsimile')))
        self.hours = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:HoursOfService')))
        self.instructions = testXMLValue(self._root.find(ns_ows('ows:ContactInfo/ows:ContactInstructions')))
        self.organization = testXMLValue(self._root.find(ns_ows('ows:ContactPersonPrimary/ows:ContactOrganization')))
        self.url = testXMLValue(self._root.find(nspath_eval('ows:ContactInfo/ows:nlineResource', namespaces)).attrib.get(nspath_eval('xlink:href', namespaces), True))
        """
