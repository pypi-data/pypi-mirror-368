from typing import Generic
from maleo.soma.mixins.parameter import (
    IdentifierTypeT,
    IdentifierType,
    IdentifierValueT,
    IdentifierValue,
    OptionalListOfDataStatuses,
    UseCache,
)


class ReadSingleQueryParameterSchema(
    OptionalListOfDataStatuses,
    UseCache,
):
    pass


class BaseReadSingleParameterSchema(
    UseCache,
    IdentifierValue[IdentifierValueT],
    IdentifierType[IdentifierTypeT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass


class ReadSingleParameterSchema(
    OptionalListOfDataStatuses,
    BaseReadSingleParameterSchema[IdentifierTypeT, IdentifierValueT],
    Generic[IdentifierTypeT, IdentifierValueT],
):
    pass
