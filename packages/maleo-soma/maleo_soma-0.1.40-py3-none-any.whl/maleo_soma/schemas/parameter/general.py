from typing import Generic
from pydantic import BaseModel
from maleo_soma.mixins.parameter import (
    IdentifierTypeT,
    IdentifierType,
    IdentifierValueT,
    IdentifierValue,
    OptionalListOfDataStatuses,
)


class ReadSingleQueryParameterSchema(
    OptionalListOfDataStatuses,
    BaseModel,
):
    pass


class BaseReadSingleParameterSchema(
    IdentifierValue[IdentifierValueT],
    IdentifierType[IdentifierTypeT],
    BaseModel,
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class ReadSingleParameterSchema(
    OptionalListOfDataStatuses,
    BaseReadSingleParameterSchema[IdentifierTypeT, IdentifierValueT],
    BaseModel,
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass
