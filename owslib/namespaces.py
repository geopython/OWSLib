
class OWSLibNamespaces(object):
    ''' Class for holding and maniputlating a dictionary containing the various namespaces for
         each standard.
    '''
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
        'gml311': 'http://www.opengis.net/gml',
        'gml32': 'http://www.opengis.net/gml/3.2',
        'gmx': 'http://www.isotc211.org/2005/gmx',
        'gts': 'http://www.isotc211.org/2005/gts',
        'ogc': 'http://www.opengis.net/ogc',
        'om10' : 'http://www.opengis.net/om/1.0',
        'ows': 'http://www.opengis.net/ows',
        'ows100': 'http://www.opengis.net/ows',
        'ows110': 'http://www.opengis.net/ows/1.1',
        'ows200': 'http://www.opengis.net/ows/2.0',
        'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
        'sml': 'http://www.opengis.net/sensorML/1.0.1',
        'sos': 'http://www.opengis.net/sos/1.0',
        'srv': 'http://www.isotc211.org/2005/srv',
        'swe': 'http://www.opengis.net/swe/1.0.1',
        'swe10': 'http://www.opengis.net/swe/1.0',
        'swe101': 'http://www.opengis.net/swe/1.0.1',
        'swe200': 'http://www.opengis.net/swe/2.0',
        'wfs': 'http://www.opengis.net/wfs',
        'wcs': 'http://www.opengis.net/wcs',
        'wps': 'http://www.opengis.net/wps/1.0.0',
        'wps100': 'http://www.opengis.net/wps/1.0.0',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xs' : 'http://www.w3.org/2001/XMLSchema',
        'xs2': 'http://www.w3.org/XML/Schema',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        #None: 'http://www.opengis.net/ogc' 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/' 'http://www.isotc211.org/2005/gmd'
    }    

    def get_namespace(self, key):
        '''Retrieves a namespace from the dictionary
            For Example:
            
            >>> ns = OWSLibNamespaces()
            >>> ns.get_namespace('csw')
            'http://www.opengis.net/cat/csw/2.0.2'
        '''
        retval = None
        if key in self.namespace_dict.keys():
            retval = self.namespace_dict[key]
        return retval
    
    def get_versioned_namespace(self, key, ver=None):
        '''Retrieves a namespace from the dictionary with a specific version number
            For Example:
            
            >>> ns = OWSLibNamespaces()
            >>> ns.get_versioned_namespace('ows')
            'http://www.opengis.net/ows'
            >>> ns.get_versioned_namespace('ows','1.1.0')
            'http://www.opengis.net/ows/1.1'
        '''
        
        if ver is None:
            return self.get_namespace(key)

        version = ''
        # Strip the decimals out of the passed in version
        for s in ver.split('.'):
            version += s
        
        key += version

        retval = None
        if key in self.namespace_dict.keys():
            retval = self.namespace_dict[key]
            
        return retval
    
    def get_dict_namespaces(self, keys=None):
        keys = keys if keys is not None else []
        retval = {}
        for key in keys:
            if key in self.namespace_dict.keys():
                retval[key] = self.namespace_dict[key]
                
        return retval


    def get_namespaces(self,keys=None):
        '''Retrieves a list of namespaces from the dictionary
            For Example:
            
            >>> ns = OWSLibNamespaces()
            >>> ns.get_namespaces(['csw','gmd'])
            ['http://www.opengis.net/cat/csw/2.0.2', 'http://www.isotc211.org/2005/gmd']
            >>> ns.get_namespaces()
            {...}
        '''

        keys = keys if keys is not None else []
        retval = []
        # if we aren't looking for namespaces in particular, return the whole dict
        if len(keys) < 1:
            retval = self.namespace_dict
        else:
        # iterate through the dictionary getting our namespaces
            for key in keys:
                if key in self.namespace_dict.keys():
                    retval.append(self.namespace_dict[key])
                else:
                    retval.append(None)
        
        return retval
    