from typing import Generic
from maleo_soma.mixins.parameter import (
    IdentifierTypeT,
    IdentifierType,
    IdentifierValueT,
    IdentifierValue,
    OptionalListOfDataStatuses,
)


class ReadSingleQueryParameterSchema(
    OptionalListOfDataStatuses,
):
    pass


class BaseReadSingleParameterSchema(
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
