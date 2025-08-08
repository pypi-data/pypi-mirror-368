from typing import Literal, Optional
from maleo_soma.enums.execution import Execution

type SyncExecutionLiteral = Literal[Execution.SYNC]

type OptionalSyncExecutionLiteral = Optional[SyncExecutionLiteral]

type AsyncExecutionLiteral = Literal[Execution.ASYNC]

type OptionalAsyncExecutionLiteral = Optional[AsyncExecutionLiteral]

type ExecutionLiteral = Literal[Execution.SYNC, Execution.ASYNC]

type OptionalExecutionLiteral = Optional[ExecutionLiteral]
