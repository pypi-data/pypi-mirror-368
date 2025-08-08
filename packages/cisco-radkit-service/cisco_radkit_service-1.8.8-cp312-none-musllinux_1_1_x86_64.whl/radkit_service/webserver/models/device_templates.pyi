from _typeshed import Incomplete
from pydantic import computed_field
from radkit_service.database.models import DbDeviceTemplate, DbVariableDefinition
from radkit_service.webserver.models.base import RADKitBaseModel, RADKitRootModel, UpdateField
from radkit_service.webserver.models.devices import NewExternalSourceProtocolsDefinition
from typing import Any

__all__ = ['StoredDeviceTemplate', 'NewDeviceTemplate', 'DeleteDeviceTemplates', 'UpdateDeviceTemplate', 'NewVariableDefinition']

class StoredVariableDefinition(RADKitBaseModel):
    name: str
    description: str
    defaultValue: str | None
    @classmethod
    def from_db_variable_definition(cls, db_variable_definition: DbVariableDefinition) -> StoredVariableDefinition: ...

class StoredDeviceTemplate(RADKitBaseModel):
    name: str
    description: str
    variableDefinitions: list[StoredVariableDefinition]
    protocolsDefinitionTemplate: str
    @computed_field
    def warnings(self) -> list[str]: ...
    @computed_field
    def errors(self) -> list[str]: ...
    @classmethod
    def from_db_device_template(cls, db_device_template: DbDeviceTemplate) -> StoredDeviceTemplate: ...

class NewVariableDefinition(RADKitBaseModel):
    name: str
    description: str
    defaultValue: str | None

class NewDeviceTemplate(RADKitBaseModel):
    name: str
    description: str
    variableDefinitions: list[NewVariableDefinition]
    protocolsDefinitionTemplate: NewExternalSourceProtocolsDefinition
    @classmethod
    def preprocess_external_source_protocols_definition(cls, value: str | dict[str, Any] | None) -> Any: ...

class UpdateDeviceTemplate(RADKitBaseModel):
    name: str
    description: UpdateField[str]
    variableDefinitions: UpdateField[list[NewVariableDefinition]]
    protocolsDefinitionTemplate: NewExternalSourceProtocolsDefinition
    @classmethod
    def preprocess_external_source_protocols_definition(cls, value: str | dict[str, Any] | None) -> Any: ...

class DeleteDeviceTemplates(RADKitRootModel[list[str]]):
    root: list[str]
    model_config: Incomplete
