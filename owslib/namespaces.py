
class OWSLibNamespaces(object):
    #TODO: several of the namespaces had a default 'None' value, must figure out how to incorporate these
    namespace_dict = {
        'csw': 'http://www.opengis.net/cat/csw/2.0.2',
        'dc' : 'http://purl.org/dc/elements/1.1/',
        'dct': 'http://purl.org/dc/terms/',
        'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
        'fes': 'http://www.opengis.net/fes/2.0',
        'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
        'gco': 'http://www.isotc211.org/2005/gco',
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'gml': 'http://www.opengis.net/gml',
        'gml32': 'http://www.opengis.net/gml/3.2',
        'gmx': 'http://www.isotc211.org/2005/gmx',
        'gts': 'http://www.isotc211.org/2005/gts',
        'ogc': 'http://www.opengis.net/ogc',
        'ows100': 'http://www.opengis.net/ows',
        'ows110': 'http://www.opengis.net/ows/1.1',
        'ows200': 'http://www.opengis.net/ows/2.0',
        'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
        'sos': 'http://www.opengis.net/sos/1.0',
        'srv': 'http://www.isotc211.org/2005/srv',
        'wfs': 'http://www.opengis.net/wfs',
        'wcs': '{http://www.opengis.net/wcs}',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xs' : 'http://www.w3.org/2001/XMLSchema',
        'xs2': 'http://www.w3.org/XML/Schema',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        #None: 'http://www.opengis.net/ogc' 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/' 'http://www.isotc211.org/2005/gmd'
    }    

    def get_namespace(self, key):
        '''Retrieves a namespace from the dictionary
        '''
        retval = None
        if key in self.namespace_dict.keys():
            retval = self.namespace_dict[key]
        return retval
    
    def get_versioned_namespace(self, key, ver='1.0.0'):
        '''Retrieves a namespace from the dictionary with a specific version number
        '''
        #split the version and recombine it w/o decimals
        #realized that this is kinda unecessary, but it makes things slightly easier to read
        version = ''
        for s in ver.split('.'):
            version += s
        # add the version to the key and see if it exists in dict
        # else check to see if the key exists w/o the version string
        retval = None
        verkey = key + version
        if verkey in self.namespace_dict.keys():
            retval = self.namespace_dict[verkey]
        elif key in self.namespace_dict.keys():
            retval = self.namespace_dict[key]
            
        return retval
    
    def get_namespaces(self,keys=[]):
        '''Retrieves a list of namespaces from the dictionary
        '''
        retval = []
        
        if len(keys) < 1:
            retval = self.namespace_dict
        else:
            for key in keys:
                if key in self.namespace_dict.keys():
                    retval.append(self.namespace_dict[key])
                else:
                    retval.append(None)
        
        return retval
#=============================================================================== 
#    # function returns list of commonly used strings for namespaces and the like
#    def Namespaces(self):
#        return {
#            'gml': 'http://www.opengis.net/gml',
#            'ogc': 'http://www.opengis.net/ogc',
#            'ows': 'http://www.opengis.net/ows',
#            'ows11': 'http://www.opengis.net/ows/1.1',
#            'ows20': 'http://www.opengis.net/ows/2.0',
#            'wfs': 'http://www.opengis.net/wfs',
#            'wcs': '{http://www.opengis.net/wcs}',
#            'fes': 'http://www.opengis.net/fes/2.0',
#            'csw': 'http://www.opengis.net/cat/csw/2.0.2',
#            'dc' : 'http://purl.org/dc/elements/1.1/',
#            'dct': 'http://purl.org/dc/terms/',
#            'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
#            'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
#            'gco': 'http://www.isotc211.org/2005/gco',
#            'gmd': 'http://www.isotc211.org/2005/gmd',
#            'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
#            'xs' : 'http://www.w3.org/2001/XMLSchema',
#            'xs2': 'http://www.w3.org/XML/Schema',
#            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
#            'xlink': 'http://www.w3.org/1999/xlink',
#            None: 'http://www.opengis.net/ogc'
#        }
#    
#    def WFSNamespaces(self):
#        return {
#            'gml': 'http://www.opengis.net/gml',
#            'ogc': 'http://www.opengis.net/ogc',
#            'ows': 'http://www.opengis.net/ows',
#            'wfs': 'http://www.opengis.net/wfs'
#        }
#    
#    def CSWNamespaces(self):
#        return {
#            'csw': 'http://www.opengis.net/cat/csw/2.0.2',
#            'dc' : 'http://purl.org/dc/elements/1.1/',
#            'dct': 'http://purl.org/dc/terms/',
#            'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
#            'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
#            'gco': 'http://www.isotc211.org/2005/gco',
#            'gmd': 'http://www.isotc211.org/2005/gmd',
#            'gml': 'http://www.opengis.net/gml',
#            'ogc': 'http://www.opengis.net/ogc',
#            'ows': 'http://www.opengis.net/ows',
#            'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
#            'xs' : 'http://www.w3.org/2001/XMLSchema',
#            'xs2': 'http://www.w3.org/XML/Schema',
#            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
#        }
#===============================================================================