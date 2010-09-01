#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2010 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================

""" FGDC metadata parser """

from owslib.etree import etree
from owslib import util

class Metadata(object):
    """ Process metadata """
    def __init__(self, md):
        self.idinfo = Idinfo(md)
        self.eainfo = Eainfo(md)
        self.metainfo = Metainfo(md)

class Idinfo(object):
    """ Process idinfo """
    def __init__(self, md):
        val = md.find('idinfo/datasetid')
        self.datasetid = util.testXMLValue(val)

        val = md.find('idinfo/citation')
        self.citation = Citation(val)

        val = md.find('idinfo/descript')
        self.descript = Descript(val)

        val = md.find('idinfo/timeperd')
        self.timeperd = Timeperd(val)

        val = md.find('idinfo/status')
        self.status = Status(val)

        val = md.find('idinfo/spdom')
        self.spdom = Spdom(val)

        val = md.find('idinfo/keywords')
        self.keywords = Keywords(val)

        val = md.find('idinfo/accconst')
        self.accconst = util.testXMLValue(val)

        val = md.find('idinfo/useconst')
        self.useconst = util.testXMLValue(val)

        val = md.find('idinfo/ptcontac')
        self.ptcontac = Ptcontac(val)

        val = md.find('idinfo/datacred')
        self.datacred = util.testXMLValue(val)

        val = md.find('idinfo/crossref')
        self.crossref = Citation(val)

class Citation(object):
    """ Process citation """
    def __init__(self, md):
        if md is not None:
            self.citeinfo = {}
    
            val = md.find('citeinfo/origin')
            self.citeinfo['origin'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/pubdate')
            self.citeinfo['pubdate'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/title')
            self.citeinfo['title'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/geoform')
            self.citeinfo['geoform'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/pubinfo/pubplace')
            self.citeinfo['pubplace'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/pubinfo/publish')
            self.citeinfo['publish'] = util.testXMLValue(val)
    
            val = md.find('citeinfo/onlink')
            self.citeinfo['onlink'] = util.testXMLValue(val)

class Descript(object):
    """ Process descript """
    def __init__(self, md):
        val = md.find('abstract')
        self.abstract = util.testXMLValue(val)
        
        val = md.find('purpose')
        self.abstract = util.testXMLValue(val)

        val = md.find('supplinf')
        self.supplinf = util.testXMLValue(val)

class Timeperd(object):
    """ Process timeperd """
    def __init__(self, md):
        if md is not None:
            val = md.find('timeinfo/sngdate/caldate')
            self.caldate = util.testXMLValue(val)

            val = md.find('current')
            self.current = util.testXMLValue(val)

class Status(object):
    """ Process status """
    def __init__(self, md):
        val = md.find('progress')
        self.progress = util.testXMLValue(val)

        val = md.find('update')
        self.update = util.testXMLValue(val)

class Spdom(object):
    """ Process spdom """
    def __init__(self, md):
        val = md.find('bounding/westbc')
        self.westbc = util.testXMLValue(val)

        val = md.find('bounding/eastbc')
        self.eastbc = util.testXMLValue(val)
       
        val = md.find('bounding/northbc')
        self.northbc = util.testXMLValue(val)

        val = md.find('bounding/southbc')
        self.southbc = util.testXMLValue(val)

class Keywords(object):
    """ Process keywords """
    def __init__(self, md):
        self.theme = []
        self.place = []
        self.temporal = []

        for i in md.findall('theme'):
            theme = {}
            val = i.find('themekt')
            theme['themekt'] = util.testXMLValue(val)
            theme['themekey'] = []
            for j in i.findall('themekey'):
                theme['themekey'].append(util.testXMLValue(j))
            self.theme.append(theme)

        for i in md.findall('place'):
            theme = {}
            place = {}
            val = i.find('placekt')
            theme['placekt'] = util.testXMLValue(val)
            theme['placekey'] = []
            for j in i.findall('placekey'):
                theme['placekey'].append(util.testXMLValue(j))
            self.place.append(place)

        for i in md.findall('temporal'):
            theme = {}
            temporal = {}
            val = i.find('tempkt')
            theme['tempkt'] = util.testXMLValue(val)
            theme['tempkey'] = []
            for j in i.findall('tempkey'):
                theme['tempkey'].append(util.testXMLValue(j))
            self.temporal.append(temporal)

class Ptcontac(object):
    """ Process ptcontac """
    def __init__(self, md):
        val = md.find('cntinfo/cntorgp/cntorg')
        self.cntorg = util.testXMLValue(val)    

        val = md.find('cntinfo/cntorgp/cntper')
        self.cntper = util.testXMLValue(val)    

        val = md.find('cntinfo/cntpos')
        self.cntpos = util.testXMLValue(val)    

        val = md.find('cntinfo/cntaddr/addrtype')
        self.addrtype = util.testXMLValue(val)

        val = md.find('cntinfo/cntaddr/address')
        self.address = util.testXMLValue(val)

        val = md.find('cntinfo/cntaddr/city')
        self.city = util.testXMLValue(val)

        val = md.find('cntinfo/cntaddr/state')
        self.state = util.testXMLValue(val)

        val = md.find('cntinfo/cntaddr/postal')
        self.postal = util.testXMLValue(val)

        val = md.find('cntinfo/cntaddr/country')
        self.country = util.testXMLValue(val)

        val = md.find('cntinfo/cntvoice')
        self.voice = util.testXMLValue(val)

        val = md.find('cntinfo/cntemail')
        self.email = util.testXMLValue(val)

class Eainfo(object):
    """ Process eainfo """
    def __init__(self, md):
        val = md.find('eainfo/detailed/enttyp/enttypl')
        self.enttypl = util.testXMLValue(val)

        val = md.find('eainfo/detailed/enttyp/enttypd')
        self.enttypd = util.testXMLValue(val)

        val = md.find('eainfo/detailed/enttyp/enttypds')
        self.enttypds = util.testXMLValue(val)

        self.attr = []
        for i in md.findall('eainfo/detailed/attr'):
            attr = {}
            val = i.find('attrlabl')
            attr['attrlabl'] = util.testXMLValue(val)

            val = i.find('attrdef')
            attr['attrdef'] = util.testXMLValue(val)

            val = i.find('attrdefs')
            attr['attrdefs'] = util.testXMLValue(val)

            val = i.find('attrdomv/udom')
            attr['udom'] = util.testXMLValue(val)

            self.attr.append(attr)

class Metainfo(object):
    """ Process metainfo """
    def __init__(self, md):
        val = md.find('metainfo/metd')
        self.metd = util.testXMLValue(val)

        val = md.find('metainfo/metrd')
        self.metrd = util.testXMLValue(val)

        val = md.find('metainfo/metc')        
        self.metc = Ptcontac(val)

        val = md.find('metainfo/metstdn')
        self.metstdn = util.testXMLValue(val)

        val = md.find('metainfo/metstdv')
        self.metstdv = util.testXMLValue(val)

        val = md.find('metainfo/metac')
        self.metac = util.testXMLValue(val)

        val = md.find('metainfo/metuc')
        self.metuc = util.testXMLValue(val)
