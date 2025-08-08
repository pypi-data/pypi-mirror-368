from typing import Any, Generic, Literal
from maleo_soma.mixins.general import SuccessT
from maleo_soma.enums.operation import OperationType
from maleo_soma.schemas.error import (
    NoErrorMixin,
    ErrorMixin,
)
from maleo_soma.schemas.operation.base import BaseOperationSchema
from maleo_soma.schemas.operation.result import (
    AnyOperationResultMixin,
    NoOperationResultMixin,
    OptionalOperationResultMixin,
)
from .action import SystemOperationActionSchema


class SystemOperationSchema(
    AnyOperationResultMixin,
    BaseOperationSchema[SuccessT, SystemOperationActionSchema],
    Generic[SuccessT],
):
    type: OperationType = OperationType.SYSTEM


class FailedSystemOperationSchema(
    NoOperationResultMixin, ErrorMixin, SystemOperationSchema[Literal[False]]
):
    success: Literal[False] = False


class SuccessfulSystemOperationSchema(
    OptionalOperationResultMixin[Any],
    NoErrorMixin,
    SystemOperationSchema[Literal[True]],
):
    success: Literal[True] = True
