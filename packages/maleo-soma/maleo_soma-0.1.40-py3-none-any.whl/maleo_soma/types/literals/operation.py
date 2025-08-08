from typing import Literal, Optional
from maleo_soma.enums.operation import (
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationStatusUpdateType,
)

# Operation type

type CreateResourceOperationTypeLiteral = Literal[ResourceOperationType.CREATE]

type OptionalCreateResourceOperationTypeLiteral = Optional[
    CreateResourceOperationTypeLiteral
]

type ReadResourceOperationTypeLiteral = Literal[ResourceOperationType.READ]

type OptionalReadResourceOperationTypeLiteral = Optional[
    ReadResourceOperationTypeLiteral
]

type UpdateResourceOperationTypeLiteral = Literal[ResourceOperationType.UPDATE]

type OptionalUpdateResourceOperationTypeLiteral = Optional[
    UpdateResourceOperationTypeLiteral
]

type DeleteResourceOperationTypeLiteral = Literal[ResourceOperationType.DELETE]

type OptionalDeleteResourceOperationTypeLiteral = Optional[
    DeleteResourceOperationTypeLiteral
]

type ResourceOperationTypeLiteral = Literal[
    ResourceOperationType.CREATE,
    ResourceOperationType.READ,
    ResourceOperationType.UPDATE,
    ResourceOperationType.DELETE,
]

type OptionalResourceOperationTypeLiteral = Optional[ResourceOperationTypeLiteral]

# Operation create type

type NewCreateResourceOperationCreateTypeLiteral = Literal[
    ResourceOperationCreateType.NEW
]

type OptionalNewCreateResourceOperationCreateTypeLiteral = Optional[
    NewCreateResourceOperationCreateTypeLiteral
]

type RestoreCreateResourceOperationCreateTypeLiteral = Literal[
    ResourceOperationCreateType.RESTORE
]

type OptionalRestoreCreateResourceOperationCreateTypeLiteral = Optional[
    RestoreCreateResourceOperationCreateTypeLiteral
]

type ResourceOperationCreateTypeLiteral = Literal[
    ResourceOperationCreateType.NEW, ResourceOperationCreateType.RESTORE
]

type OptionalResourceOperationCreateTypeLiteral = Optional[
    ResourceOperationCreateTypeLiteral
]

# Operation update type

type DataUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationUpdateType.DATA
]

type OptionalDataUpdateResourceOperationUpdateTypeLiteral = Optional[
    DataUpdateResourceOperationUpdateTypeLiteral
]

type StatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationUpdateType.STATUS
]

type OptionalStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    StatusUpdateResourceOperationUpdateTypeLiteral
]

type ResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationUpdateType.DATA,
    ResourceOperationUpdateType.STATUS,
]

type OptionalResourceOperationUpdateTypeLiteral = Optional[
    ResourceOperationUpdateTypeLiteral
]

# Operation status update type

type ActivateStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.ACTIVATE
]

type OptionalActivateStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    ActivateStatusUpdateResourceOperationUpdateTypeLiteral
]

type DeactivateStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.DEACTIVATE
]

type OptionalDeactivateStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    DeactivateStatusUpdateResourceOperationUpdateTypeLiteral
]

type RestoreStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.RESTORE
]

type OptionalRestoreStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    RestoreStatusUpdateResourceOperationUpdateTypeLiteral
]

type DeleteStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.DELETE
]

type OptionalDeleteStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    DeleteStatusUpdateResourceOperationUpdateTypeLiteral
]

type ResourceOperationStatusUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.ACTIVATE,
    ResourceOperationStatusUpdateType.DEACTIVATE,
    ResourceOperationStatusUpdateType.RESTORE,
    ResourceOperationStatusUpdateType.DELETE,
]

type OptionalResourceOperationStatusUpdateTypeLiteral = Optional[
    ResourceOperationStatusUpdateTypeLiteral
]
