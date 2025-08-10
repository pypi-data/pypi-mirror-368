from pydantic import BaseModel, Field
from maleo_soma.enums.environment import Environment
from maleo_soma.enums.logging import LoggerType
from maleo_soma.enums.service import Service
from maleo_soma.types.base import OptionalString


class LogLabels(BaseModel):
    logger_type: LoggerType = Field(..., description="Logger's type")
    service_environment: Environment = Field(..., description="Service's environment")
    service_key: Service = Field(..., description="Service's key")
    client_key: OptionalString = Field(None, description="Client's key (Optional)")
