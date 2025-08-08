from datetime import date, datetime
from typing import Any, Dict, Literal, List, Mapping, Optional, Sequence, Union
from uuid import UUID
from maleo_soma.enums.pagination import Limit
from maleo_soma.enums.status import DataStatus


# Any-related types
type ListOfAny = List[Any]
type SequenceOfAny = Sequence[Any]
type OptionalAny = Optional[Any]

# Boolean-related types
type LiteralFalse = Literal[False]
type LiteralTrue = Literal[True]
type ListOfBools = List[bool]
type SequenceOfBools = Sequence[bool]
type OptionalBoolean = Optional[bool]

# Float-related types
type ListOfFloats = List[float]
type SequenceOfFloats = Sequence[float]
type OptionalFloat = Optional[float]
type OptionalListOfFloats = Optional[List[float]]
type OptionalSequenceOfFloats = Optional[Sequence[float]]

# Integer-related types
type ListOfIntegers = List[int]
type SequenceOfIntegers = Sequence[int]
type OptionalInteger = Optional[int]
type OptionalListOfIntegers = Optional[List[int]]
type OptionalSequenceOfIntegers = Optional[Sequence[int]]


# Bytes-related types
type OptionalBytes = Optional[bytes]

# String-related types
type ListOfStrings = List[str]
type SequenceOfStrings = Sequence[str]
type OptionalString = Optional[str]
type OptionalListOfStrings = Optional[List[str]]
type OptionalSequenceOfStrings = Optional[Sequence[str]]

# Date-related types
type OptionalDate = Optional[date]

# Datetime-related types
type OptionalDatetime = Optional[datetime]

# Any Dict-related types
type StringToAnyDict = Dict[str, Any]
type OptionalStringToAnyDict = Optional[Dict[str, Any]]
type ListOfStringToAnyDict = List[Dict[str, Any]]
type SequenceOfStringToAnyDict = Sequence[Dict[str, Any]]
type OptionalListOfStringToAnyDict = Optional[List[Dict[str, Any]]]
type OptionalSequenceOfStringToAnyDict = Optional[Sequence[Dict[str, Any]]]
type StringToObjectDict = Dict[str, object]
type OptionalStringToObjectDict = Optional[Dict[str, object]]
type ListOfStringToObjectDict = List[Dict[str, object]]
type SequenceOfStringToObjectDict = Sequence[Dict[str, object]]
type OptionalListOfStringToObjectDict = Optional[List[Dict[str, object]]]
type OptionalSequenceOfStringToObjectDict = Optional[Sequence[Dict[str, object]]]
type IntToAnyDict = Dict[int, Any]
type OptionalIntToAnyDict = Optional[Dict[int, Any]]
type ListOfIntToAnyDict = List[Dict[int, Any]]
type SequenceOfIntToAnyDict = Sequence[Dict[int, Any]]
type OptionalListOfIntToAnyDict = Optional[List[Dict[int, Any]]]
type OptionalSequenceOfIntToAnyDict = Optional[Sequence[Dict[int, Any]]]

# Any Mapping-related types
type StringToAnyMapping = Mapping[str, Any]
type OptionalStringToAnyMapping = Optional[Mapping[str, Any]]
type ListOfStringToAnyMapping = List[Mapping[str, Any]]
type SequenceOfStringToAnyMapping = Sequence[Mapping[str, Any]]
type OptionalListOfStringToAnyMapping = Optional[List[Mapping[str, Any]]]
type OptionalSequenceOfStringToAnyMapping = Optional[Sequence[Mapping[str, Any]]]
type StringToObjectMapping = Mapping[str, object]
type OptionalStringToObjectMapping = Optional[Mapping[str, object]]
type ListOfStringToObjectMapping = List[Mapping[str, object]]
type SequenceOfStringToObjectMapping = Sequence[Mapping[str, object]]
type OptionalListOfStringToObjectMapping = Optional[List[Mapping[str, object]]]
type OptionalSequenceOfStringToObjectMapping = Optional[Sequence[Mapping[str, object]]]
type IntToAnyMapping = Mapping[int, Any]
type OptionalIntToAnyMapping = Optional[Mapping[int, Any]]
type ListOfIntToAnyMapping = List[Mapping[int, Any]]
type SequenceOfIntToAnyMapping = Sequence[Mapping[int, Any]]
type OptionalListOfIntToAnyMapping = Optional[List[Mapping[int, Any]]]
type OptionalSequenceOfIntToAnyMapping = Optional[Sequence[Mapping[int, Any]]]

# String Dict-related types
type StringToStringDict = Dict[str, str]
type OptionalStringToStringDict = Optional[Dict[str, str]]
type ListOfStringToStringDict = List[Dict[str, str]]
type SequenceOfStringToStringDict = Sequence[Dict[str, str]]
type OptionalListOfStringToStringDict = Optional[List[Dict[str, str]]]
type OptionalSequenceOfStringToStringDict = Optional[Sequence[Dict[str, str]]]
type IntToStringDict = Dict[int, str]
type OptionalIntToStringDict = Optional[Dict[int, str]]
type ListOfIntToStringDict = List[Dict[int, str]]
type SequenceOfIntToStringDict = Sequence[Dict[int, str]]
type OptionalListOfIntToStringDict = Optional[List[Dict[int, str]]]
type OptionalSequenceOfIntToStringDict = Optional[Sequence[Dict[int, str]]]

# String Mapping-related types
type StringToStringMapping = Mapping[str, str]
type OptionalStringToStringMapping = Optional[Mapping[str, str]]
type ListOfStringToStringMapping = List[Mapping[str, str]]
type SequenceOfStringToStringMapping = Sequence[Mapping[str, str]]
type OptionalListOfStringToStringMapping = Optional[List[Mapping[str, str]]]
type OptionalSequenceOfStringToStringMapping = Optional[Sequence[Mapping[str, str]]]
type IntToStringMapping = Mapping[int, str]
type OptionalIntToStringMapping = Optional[Mapping[int, str]]
type ListOfIntToStringMapping = List[Mapping[int, str]]
type SequenceOfIntToStringMapping = Sequence[Mapping[int, str]]
type OptionalListOfIntToStringMapping = Optional[List[Mapping[int, str]]]
type OptionalSequenceOfIntToStringMapping = Optional[Sequence[Mapping[int, str]]]

# List Dict-related types
type StringToListOfStringDict = Dict[str, List[str]]
type StringToSequenceOfStringDict = Dict[str, Sequence[str]]
type OptionalStringToListOfStringDict = Optional[Dict[str, List[str]]]
type OptionalStringToSequenceOfStringDict = Optional[Dict[str, Sequence[str]]]

# List Mapping-related types
type StringToListOfStringMapping = Mapping[str, List[str]]
type StringToSequenceOfStringMapping = Mapping[str, Sequence[str]]
type OptionalStringToListOfStringMapping = Optional[Mapping[str, List[str]]]
type OptionalStringToSequenceOfStringMapping = Optional[Mapping[str, Sequence[str]]]

# UUID-related types
type ListOfUUIDs = List[UUID]
type SequenceOfUUIDs = Sequence[UUID]
type OptionalUUID = Optional[UUID]
type OptionalListOfUUIDs = Optional[List[UUID]]
type OptionalSequenceOfUUIDs = Optional[Sequence[UUID]]

# DataStatuses-related types
type ListOfDataStatuses = List[DataStatus]
type SequenceOfDataStatuses = Sequence[DataStatus]
type OptionalListOfDataStatuses = Optional[List[DataStatus]]
type OptionalSequenceOfDataStatuses = Optional[Sequence[DataStatus]]

# Limit-related types
type OptionalLimit = Limit

# Miscellanous types
type BytesOrString = Union[bytes, str]
type OptionalBytesOrString = Optional[BytesOrString]
type IdentifierValue = Union[int, UUID, str]
type ListOrDictOfAny = Union[List[Any], Dict[str, Any]]
type SequenceOrDictOfAny = Union[Sequence[Any], Dict[str, Any]]
type ListOrMappingOfAny = Union[List[Any], Mapping[str, Any]]
type SequenceOrMappingOfAny = Union[Sequence[Any], Mapping[str, Any]]
type OptionalListOrDictOfAny = Optional[Union[List[Any], Dict[str, Any]]]
type OptionalSequenceOrDictOfAny = Optional[Union[Sequence[Any], Dict[str, Any]]]
type OptionalListOrMappingOfAny = Optional[Union[List[Any], Mapping[str, Any]]]
type OptionalSequenceOrMappingOfAny = Optional[Union[Sequence[Any], Mapping[str, Any]]]
