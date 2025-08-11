from pathlib import Path
from typing import Optional
from maleo_soma.dtos.configurations import ConfigurationDTO
from maleo_soma.dtos.configurations.pubsub.publisher import (
    AdditionalTopicsConfigurationDTO,
)
from maleo_soma.dtos.settings import Settings
from maleo_soma.enums.secret import SecretFormat
from maleo_soma.managers.client.google.secret import GoogleSecretManager
from maleo_soma.types.base import OptionalUUID
from maleo_soma.utils.loaders.yaml import from_path, from_string


class ConfigurationManager:
    def __init__(
        self,
        settings: Settings,
        secret_manager: GoogleSecretManager,
        additional_topics_configurations: Optional[AdditionalTopicsConfigurationDTO],
        operation_id: OptionalUUID = None,
    ) -> None:
        use_local = settings.USE_LOCAL_CONFIGURATIONS
        config_path = settings.CONFIGURATIONS_PATH

        if use_local and config_path is not None and isinstance(config_path, str):
            config_path = Path(config_path)
            if config_path.exists() and config_path.is_file():
                data = from_path(config_path)
                self.configurations = ConfigurationDTO.model_validate(data)
                self.configurations.pubsub.publisher.topics.additional = (
                    additional_topics_configurations
                )
                return

        name = f"{settings.SERVICE_KEY}-configurations-{settings.ENVIRONMENT}"
        read_secret = secret_manager.read(
            SecretFormat.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.old.value)
        self.configurations = ConfigurationDTO.model_validate(data)
        self.configurations.pubsub.publisher.topics.additional = (
            additional_topics_configurations
        )
