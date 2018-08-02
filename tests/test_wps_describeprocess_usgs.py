from tests.utils import resource_file
from owslib.wps import WebProcessingService


def test_wps_describeprocess_usgs():
    # Initialize WPS client
    wps = WebProcessingService('http://cida.usgs.gov/gdp/process/WebProcessingService', skip_caps=True)
    # Execute fake invocation of DescribeProcess operation by parsing cached response from
    xml = open(resource_file('wps_USGSDescribeProcess.xml'), 'rb').read()
    process = wps.describeprocess('gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm', xml=xml)
    # Check process description
    assert process.identifier == 'gov.usgs.cida.gdp.wps.algorithm.FeatureWeightedGridStatisticsAlgorithm'
    assert process.title == 'Feature Weighted Grid Statistics'
    assert process.abstract == 'This algorithm generates area weighted statistics of a gridded dataset for a set of vector polygon features. Using the bounding-box that encloses the feature data and the time range, if provided, a subset of the gridded dataset is requested from the remote gridded data server. Polygon representations are generated for cells in the retrieved grid. The polygon grid-cell representations are then projected to the feature data coordinate reference system. The grid-cells are used to calculate per grid-cell feature coverage fractions. Area-weighted statistics are then calculated for each feature using the grid values and fractions as weights. If the gridded dataset has a time range the last step is repeated for each time step within the time range or all time steps if a time range was not supplied.'  # NOQA
    # Check process inputs
    # Expected Input:
    #     Process input:
    #  identifier=FEATURE_COLLECTION, title=Feature Collection, abstract=A feature collection encoded as a WFS request or one of the supported GML profiles., data type=ComplexData  # NOQA
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/2.0.0/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/2.1.1/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/2.1.2/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/2.1.2.1/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/3.0.0/base/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/3.0.1/base/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/3.1.0/base/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/3.1.1/base/feature.xsd
    #  Supported Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/3.2.1/base/feature.xsd
    #  Default Value: mimeType=text/xml, encoding=UTF-8, schema=http://schemas.opengis.net/gml/2.0.0/feature.xsd
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=DATASET_URI, title=Dataset URI, abstract=The base data web service URI for the dataset of interest., data type=anyURI  # NOQA
    #  Any value allowed
    #  Default Value: None
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=DATASET_ID, title=Dataset Identifier, abstract=The unique identifier for the data type or variable of interest., data type=string  # NOQA
    #  Any value allowed
    #  Default Value: None
    #  minOccurs=1, maxOccurs=2147483647
    # Process input:
    #  identifier=REQUIRE_FULL_COVERAGE, title=Require Full Coverage, abstract=If turned on, the service will require that the dataset of interest fully cover the polygon analysis zone data., data type=boolean  # NOQA
    #  Any value allowed
    #  Default Value: True
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=TIME_START, title=Time Start, abstract=The date to begin analysis., data type=dateTime
    #  Any value allowed
    #  Default Value: None
    #  minOccurs=0, maxOccurs=1
    # Process input:
    #  identifier=TIME_END, title=Time End, abstract=The date to end analysis., data type=dateTime
    #  Any value allowed
    #  Default Value: None
    #  minOccurs=0, maxOccurs=1
    # Process input:
    #  identifier=FEATURE_ATTRIBUTE_NAME, title=Feature Attribute Name, abstract=The attribute that will be used to label column headers in processing output., data type=string  # NOQA
    #  Any value allowed
    #  Default Value: None
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=DELIMITER, title=Delimiter, abstract=The delimiter that will be used to separate columns in the processing output., data type=string  # NOQA
    #  Allowed Value: COMMA
    #  Allowed Value: TAB
    #  Allowed Value: SPACE
    #  Default Value: COMMA
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=STATISTICS, title=Statistics, abstract=Statistics that will be returned for each feature in the processing output., data type=string  # NOQA
    #  Allowed Value: MEAN
    #  Allowed Value: MINIMUM
    #  Allowed Value: MAXIMUM
    #  Allowed Value: VARIANCE
    #  Allowed Value: STD_DEV
    #  Allowed Value: WEIGHT_SUM
    #  Allowed Value: COUNT
    #  Default Value: None
    #  minOccurs=1, maxOccurs=7
    # Process input:
    #  identifier=GROUP_BY, title=Group By, abstract=If multiple features and statistics are selected, this will change whether the processing output columns are sorted according to statistics or feature attributes., data type=string  # NOQA
    #  Allowed Value: STATISTIC
    #  Allowed Value: FEATURE_ATTRIBUTE
    #  Default Value: None
    #  minOccurs=1, maxOccurs=1
    # Process input:
    #  identifier=SUMMARIZE_TIMESTEP, title=Summarize Timestep, abstract=If selected, processing output will include columns with summarized statistics for all feature attribute values for each timestep, data type=boolean  # NOQA
    #  Any value allowed
    #  Default Value: True
    #  minOccurs=0, maxOccurs=1
    # Process input:
    #  identifier=SUMMARIZE_FEATURE_ATTRIBUTE, title=Summarize Feature Attribute, abstract=If selected, processing output will include a final row of statistics summarizing all timesteps for each feature attribute value, data type=boolean  # NOQA
    #  Any value allowed
    #  Default Value: True
    #  minOccurs=0, maxOccurs=1
    assert len(process.dataInputs) == 12
    input = process.dataInputs[0]
    assert input.identifier == 'FEATURE_COLLECTION'
    assert input.dataType == 'ComplexData'
    # Expected Output:
    # identifier=OUTPUT, title=Output File, abstract=A delimited text file containing requested process output., data type=ComplexData  # NOQA
    # Supported Value: mimeType=text/csv, encoding=UTF-8, schema=None
    # Default Value: mimeType=text/csv, encoding=UTF-8, schema=None
    # reference=None, mimeType=None
    # Check process outputs
    assert len(process.processOutputs) == 1
    output = process.processOutputs[0]
    assert output.identifier == 'OUTPUT'
    assert output.dataType == 'ComplexData'
