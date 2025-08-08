from .table import DbRow
from _typeshed import Incomplete
from collections.abc import Mapping
from enum import Enum
from pydantic import AnyHttpUrl, AwareDatetime, BaseModel, EmailStr, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from radkit_common.terminal_interaction import ProvisioningVariant
from radkit_common.types import ConnectionMethod, CustomSecretStr, DeviceType, ExternalSourceType, HTTPProtocol, PortRanges, TerminalCapabilities
from typing import Annotated, Any, Literal
from typing_extensions import Self
from uuid import UUID

__all__ = ['DbSecret', 'DbDevice', 'DbTerminal', 'DbNetconf', 'DbSnmp', 'DbSwagger', 'DbHttp', 'DbRemoteUser', 'DbLabel', 'DbAdmin', 'DbLoginAttempt', 'DbVersion', 'DbExternalSource', 'DbCyberArkConjur', 'DbProtocolsDefinition', 'DbExternalSourceTerminal', 'DbExternalSourceNetconf', 'DbExternalSourceSecret', 'DbExternalSourceSnmp', 'DbExternalSourceSwagger', 'DbExternalSourceHttp', 'DbCyberArkAimCcp', 'DbHashiCorpVault', 'DbExternalSourceReference', 'DbHashiCorpVaultTokenAuth', 'DbHashiCorpVaultAppRoleAuth', 'DbPlugin', 'ExternalSources', 'DbDeviceTemplate', 'DbVariableDefinition', 'DbDeviceTemplateRef', 'DbRemoteUserExternalAuth']

class SecretEngine(str, Enum):
    CUBBYHOLE = 'cubbyhole'
    KV_V1 = 'kv-v1'
    KV_V2 = 'kv-v2'

class _NestedModel(BaseModel):
    model_config: Incomplete

class _DbSecret(str): ...

DbSecret: Incomplete

class DbDevice(DbRow):
    uuid: UUID
    name: str
    host: str
    device_type: DeviceType
    description: str
    jumphost_uuid: UUID | None
    source_key: str | None
    source_dev_uuid: UUID | None
    meta_data: Mapping[Annotated[str, None], Annotated[str, None]]
    enabled: bool
    forwarded_tcp_ports: PortRanges
    terminal: DbTerminal | None
    netconf: DbNetconf | None
    snmp: DbSnmp | None
    swagger: DbSwagger | None
    http: DbHttp | None
    device_template_ref: DbDeviceTemplateRef | None
    label_ids: frozenset[int]
    import_group: str | None
    @classmethod
    def check_max_metadata_size(cls, data: dict[str, str]) -> dict[str, str]: ...

class DbTerminal(_NestedModel):
    port: int
    connection_method: Literal[ConnectionMethod.SSH, ConnectionMethod.TELNET, ConnectionMethod.SSHPUBKEY, ConnectionMethod.TELNET_NO_AUTH]
    username: str
    encrypted_password: DbSecret
    encrypted_enable_password: DbSecret
    enable_set: bool
    use_insecure_algorithms: bool
    jumphost: bool
    use_tunneling_if_jumphost: bool
    encrypted_private_key: DbSecret
    provisioning_variant: ProvisioningVariant
    capabilities: frozenset[TerminalCapabilities]

class DbNetconf(_NestedModel):
    port: int
    username: str
    encrypted_password: DbSecret
    use_insecure_algorithms: bool

class DbSnmp(_NestedModel):
    version: int
    port: int
    encrypted_community_string: DbSecret

class DbSwagger(_NestedModel):
    username: str
    encrypted_password: DbSecret
    port: int
    schema_path: str
    verify: bool
    use_insecure_algorithms: bool

class DbHttp(_NestedModel):
    port: int
    protocol: HTTPProtocol
    verify: bool
    use_insecure_algorithms: bool
    username: str
    encrypted_password: DbSecret
    authentication_extra: str | None

class TemplateStr(str):
    TEMPLATE_PATTERN: Incomplete
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema: ...
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: CoreSchema, _handler: GetJsonSchemaHandler) -> JsonSchemaValue: ...
    @classmethod
    def validate(cls, value: str) -> TemplateStr: ...

class DbExternalSourceSecret(_NestedModel):
    external_source: TemplateStr | str
    path: TemplateStr | str

class DbExternalSourceValue(_NestedModel):
    value: TemplateStr | str

class DbExternalSourceReference(_NestedModel):
    name: str
    params: Mapping[TemplateStr | str, TemplateStr | Any]

class DbExternalSourceTerminal(_NestedModel):
    external_source: DbExternalSourceReference | None
    port: int | TemplateStr
    connection_method: Literal[ConnectionMethod.SSH, ConnectionMethod.TELNET, ConnectionMethod.SSHPUBKEY, ConnectionMethod.TELNET_NO_AUTH] | TemplateStr
    use_insecure_algorithms: bool | TemplateStr
    jumphost: bool | TemplateStr
    use_tunneling_if_jumphost: bool | TemplateStr
    provisioning_variant: ProvisioningVariant | TemplateStr
    capabilities: frozenset[TerminalCapabilities | TemplateStr]
    username: DbExternalSourceSecret | DbExternalSourceValue | None
    password: DbExternalSourceSecret | None
    enable_password: DbExternalSourceSecret | None
    private_key: DbExternalSourceSecret | None

class DbExternalSourceNetconf(_NestedModel):
    external_source: DbExternalSourceReference | None
    port: int | TemplateStr
    use_insecure_algorithms: bool | TemplateStr
    username: DbExternalSourceSecret | DbExternalSourceValue | None
    password: DbExternalSourceSecret | None

class DbExternalSourceSnmp(_NestedModel):
    external_source: DbExternalSourceReference | None
    version: int | TemplateStr
    port: int | TemplateStr
    community_string: DbExternalSourceSecret | None

class DbExternalSourceSwagger(_NestedModel):
    external_source: DbExternalSourceReference | None
    port: int | TemplateStr
    schema_path: TemplateStr | str
    verify: bool | TemplateStr
    use_insecure_algorithms: bool | TemplateStr
    username: DbExternalSourceSecret | DbExternalSourceValue | None
    password: DbExternalSourceSecret | None

class DbExternalSourceHttp(_NestedModel):
    external_source: DbExternalSourceReference | None
    port: int | TemplateStr
    protocol: HTTPProtocol | TemplateStr
    verify: bool | TemplateStr
    use_insecure_algorithms: bool | TemplateStr
    authentication_extra: TemplateStr | str | None
    username: DbExternalSourceSecret | DbExternalSourceValue | None
    password: DbExternalSourceSecret | None

class DbProtocolsDefinition(_NestedModel):
    terminal: DbExternalSourceTerminal | None
    netconf: DbExternalSourceNetconf | None
    snmp: DbExternalSourceSnmp | None
    swagger: DbExternalSourceSwagger | None
    http: DbExternalSourceHttp | None

class DbRemoteUserExternalAuth(_NestedModel):
    external_source: str
    external_username: str | None

class DbRemoteUser(DbRow):
    username: str
    fullname: str
    description: str
    label_ids: frozenset[int]
    expiration_timestamp: AwareDatetime | None
    time_slice_minutes: int | None
    encrypted_access_token: DbSecret
    connection_mode_cloud_active: bool
    connection_mode_direct_active: bool
    connection_mode_direct_sso_active: bool
    external_auth: DbRemoteUserExternalAuth | None
    def is_active(self) -> bool: ...
    @classmethod
    def generate_random_access_token(cls) -> CustomSecretStr: ...

class DbLabel(DbRow):
    name: str
    color: str

class DbAdmin(DbRow):
    username: str
    password_hash: DbSecret
    password_modified_time: AwareDatetime
    require_password_change: bool
    email: Literal[''] | EmailStr
    fullname: str
    description: str
    login_attempts: tuple[DbLoginAttempt, ...]
    old_password_hashes: tuple[DbSecret, ...]
    enabled: bool
    @classmethod
    def create(cls, username: str, password: CustomSecretStr) -> Self: ...
    @classmethod
    def create_superadmin(cls) -> Self: ...
    @classmethod
    def create_hash(cls, username: str, password: CustomSecretStr) -> DbSecret: ...

class DbLoginAttempt(_NestedModel):
    succeeded: bool
    attempt_time: AwareDatetime
    ip_address: str
    user_agent: str

class DbVersion(DbRow):
    created_timestamp: AwareDatetime
    schema_revision: str
    radkit_version: str

class DbKeyboardInteractiveChallenge(_NestedModel):
    type: Literal[ExternalSourceType.KEYBOARD_INTERACTIVE_CHALLENGE]
    username: str
    encrypted_password: DbSecret
    encrypted_private_key: DbSecret

class DbCyberArkConjur(_NestedModel):
    type: Literal[ExternalSourceType.CYBERARK_CONJUR]
    base_url: AnyHttpUrl
    account: str
    username: str
    encrypted_api_key: DbSecret
    verify: bool
    use_insecure_algorithms: bool

class DbCyberArkAimCcp(_NestedModel):
    type: Literal[ExternalSourceType.CYBERARK_AIM_CCP]
    base_url: AnyHttpUrl
    app_id: str
    safe: str
    encrypted_certificate: DbSecret

class DbTacacsPlus(_NestedModel):
    type: Literal[ExternalSourceType.TACACS_PLUS]
    host: str
    port: int
    encrypted_secret: DbSecret

class DbStaticCredentials(_NestedModel):
    type: Literal[ExternalSourceType.STATIC_CREDENTIALS]
    username: str
    encrypted_password: DbSecret

class DbPlugin(_NestedModel):
    type: Literal[ExternalSourceType.PLUGIN]
    plugin_name: str

class DbHashiCorpVaultTokenAuth(_NestedModel):
    method: Literal['token']
    path: str
    encrypted_token: DbSecret

class DbHashiCorpVaultAppRoleAuth(_NestedModel):
    method: Literal['approle']
    path: str
    encrypted_role_id: DbSecret
    encrypted_secret_id: DbSecret

class DbHashiCorpVault(_NestedModel):
    type: Literal[ExternalSourceType.HASHICORP_VAULT]
    base_url: AnyHttpUrl
    engine: SecretEngine
    engine_path: str
    auth: DbHashiCorpVaultTokenAuth | DbHashiCorpVaultAppRoleAuth
    verify: bool
    use_insecure_algorithms: bool

class DbVariableDefinition(_NestedModel):
    name: str
    description: str
    default_value: str | None

class DbDeviceTemplate(DbRow):
    name: str
    description: str
    variable_definitions: tuple[DbVariableDefinition, ...]
    protocols_definition_template: DbProtocolsDefinition

class DbDeviceTemplateRef(_NestedModel):
    device_template_name: str
    device_template_variables: dict[str, str]
ExternalSources = DbKeyboardInteractiveChallenge | DbCyberArkConjur | DbCyberArkAimCcp | DbTacacsPlus | DbStaticCredentials | DbPlugin | DbHashiCorpVault

class DbExternalSource(DbRow):
    name: str
    options: ExternalSources
