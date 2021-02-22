from enum import Enum
from typing import Any, List, Union, Optional, Dict
from pydantic import BaseModel, conint, Field, AnyUrl, Extra


# Taken from the openapi schema
# https://github.com/opengeospatial/ogcapi-processes/tree/master/core/openapi/schemas

# ---- #
# Enum #
# ---- #
# Note that
# ```
# class Config:
#     use_enum_values = True
# ```
# Should be used to ensure enum are json serializable by classes that use them.


class BaseModelList(BaseModel):
    """Array-time objects defining __root__ as a list."""

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self):
        return len(self.__root__)


class Mode(Enum):
    sync = 'sync'
    async_ = 'async'
    auto = 'auto'


class Response(Enum):
    raw = 'raw'
    document = 'document'


class RangeClosure(Enum):
    closed = 'closed'
    open = 'open'
    open_closed = 'open-closed'
    closed_open = 'closed-open'


class Status(Enum):
    accepted = 'accepted'
    running = 'running'
    successful = 'successful'
    failed = 'failed'
    dismissed = 'dismissed'


class JobControlOptions(Enum):
    sync_execute = 'sync-execute'
    async_execute = 'async-execute'


class TransmissionMode(Enum):
    value = 'value'
    reference = 'reference'

# ------ #
# Values #
# ------ #


class AllowedValues(BaseModelList):
    __root__: List[Any]


class Range(BaseModel):
    class Config:
        use_enum_values = True

    minimumValue: Optional[str] = None
    maximumValue: Optional[str] = None
    spacing: Optional[str] = None
    rangeClosure: Optional[RangeClosure] = None


class AnyValue(BaseModel):
    anyValue: Optional[bool] = True


class ValuesReference(BaseModel):
    __root__: AnyUrl


class Format(BaseModel):
    # mediaType: str
    mimeType: str
    schema_: Optional[str] = Field(alias='schema', default=None)
    encoding: Optional[str] = None


class FormatDescription(Format):
    maximumMegabytes: Optional[float] = None
    default: Optional[bool] = False


class SupportedCRS(BaseModel):
    crs: Optional[str] = None
    default: Optional[bool] = False


class Metadata(BaseModel):
    title: Optional[str] = None
    role: Optional[str] = None
    href: Optional[str] = None


# ---------- #
# Parameters #
# ---------- #


class InvalidParameter(BaseModel):
    __root__: Any = Field(..., description='A query parameter has an invalid value.')


class AdditionalParameter(BaseModel):
    name: str
    value: List[Any]


class AdditionalParameters(Metadata):
    parameters: Optional[List[AdditionalParameter]] = None


# ---------- #
# Data types #
# ---------- #

class NameReferenceType(BaseModel):
    name: str
    reference: Optional[AnyUrl] = None


class LiteralDataDomain(BaseModel):
    valueDefinition: Optional[Union[AllowedValues, AnyValue, ValuesReference]] = None
    defaultValue: Optional[str] = None
    dataType: Optional[NameReferenceType] = None
    uom: Optional[NameReferenceType] = None


# TODO: Example in ogcapi-processes has `literalDataDomain`, but the schema says `literalDataDomains`
class LiteralDataType(BaseModel):
    # literalDataDomains: List[LiteralDataDomain]
    literalDataDomain: LiteralDataDomain


class ComplexDataType(BaseModel):
    formats: Optional[List[FormatDescription]] = None


class BoundingBoxDataType(BaseModel):
    supportedCRS: List[SupportedCRS]


# ---- #
# Data #
# ---- #


class BoundingBoxData(BaseModel):
    crs: Optional[AnyUrl] = None
    bbox: List[float] = Field(..., max_items=6, min_items=4)


# TODO: one of href / value is required. Need root validator.
class InlineOrRefData(BaseModel):
    dataType: Optional[NameReferenceType] = None
    uom: Optional[NameReferenceType] = None
    format: Optional[Format] = None
    href: Optional[AnyUrl] = None
    value: Optional[Union[str, float, bool, Dict[str, Any]]] = None


# -- #
# IO #
# -- #

class Input(BaseModelList):
    class Config:
        extra = Extra.allow

    # See https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
    # Forced this to be a list. Got parsing errors when allowing it to be either a List or an object.
    __root__: List[Union[InlineOrRefData, BoundingBoxData, "Input"]]


Input.update_forward_refs()


class Output(BaseModel):
    class Config:
        extra = Extra.allow

    __root__: Any


class Link(BaseModel):
    href: str
    rel: Optional[str] = Field(None, example='service')
    type: Optional[str] = Field(None, example='application/json')
    hreflang: Optional[str] = Field(None, example='en')
    title: Optional[str] = None


class LandingPage(BaseModel):
    title: Optional[str] = Field(None, example='Example processing server')
    description: Optional[str] = Field(
        None, example='Example server implementing the OGC API - Processes 1.0'
    )
    links: List[Link]


class StatusInfo(BaseModel):
    class Config:
        use_enum_values = True

    jobID: str
    status: Status
    message: Optional[str] = None
    progress: Optional[conint(ge=0, le=100)] = None
    links: Optional[List[Link]] = None


class JobList(BaseModelList):
    __root__: List[StatusInfo]


class ObservedProperty(BaseModel):
    name: Optional[str] = None
    uri: Optional[AnyUrl] = None
    description: Optional[str] = None


class DescriptionType(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[List[Metadata]] = None
    additionalParameters: Optional[AdditionalParameters] = None


class MaxOccur(BaseModel):
    pass


class InputDescription(DescriptionType):
    input: Optional[
        Union[
            ComplexDataType,
            LiteralDataType,
            BoundingBoxDataType,
        ]
    ] = None
    minOccurs: Optional[int] = None
    maxOccurs: Optional[Union[int, MaxOccur]] = None
    observedProperty: Optional[ObservedProperty] = None


class OutputDescription(DescriptionType):
    output: Optional[
        Union[ComplexDataType, LiteralDataType, BoundingBoxDataType]
    ] = None
    observedProperty: Optional[ObservedProperty] = None


class ProcessSummary(DescriptionType):
    class Config:
        use_enum_values = True

    version: str
    jobControlOptions: Optional[List[JobControlOptions]] = None
    outputTransmission: Optional[List[TransmissionMode]] = None
    links: Optional[List[Link]] = None


class Process(ProcessSummary):
    inputs: Optional[List[InputDescription]] = None
    outputs: Optional[List[OutputDescription]] = None


# Experimenting with adding dunder methods
class ProcessList(BaseModelList):
    __root__: List[ProcessSummary]


class ConfClasses(BaseModel):
    conformsTo: List[str]


class Subscriber(BaseModel):
    successUri: Optional[AnyUrl] = None
    inProgressUri: Optional[AnyUrl] = None
    failedUri: Optional[AnyUrl] = None


# TODO: id, outputs, mode and response are required according to schema
class Execute(BaseModel):
    class Config:
        use_enum_values = True

    id: Optional[str]
    inputs: Optional[Input] = None
    outputs: Optional[Output] = None
    mode: Mode
    response: Optional[Response] = None
    subscriber: Optional[Subscriber] = None


class LiteralOutput(BaseModel):
    id: str
    value: str


class Result(BaseModel):
    jobID: Optional[str]
    location: Optional[str] = None
    outputs: Optional[List[LiteralOutput]] = None
