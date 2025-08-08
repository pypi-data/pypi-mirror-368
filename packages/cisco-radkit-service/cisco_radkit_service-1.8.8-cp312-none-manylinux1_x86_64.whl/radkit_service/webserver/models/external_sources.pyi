from .base import RADKitRootModel
from _typeshed import Incomplete
from pydantic import AnyHttpUrl, ValidationInfo
from radkit_common.types import AnnotatedCustomSecretStr, CustomSecretStr, ExternalSourceAuthenticationType, ExternalSourceType
from radkit_service.database.models import DbCyberArkAimCcp, DbCyberArkConjur, DbExternalSource, DbHashiCorpVault, DbKeyboardInteractiveChallenge, DbPlugin, DbStaticCredentials, DbTacacsPlus
from radkit_service.external_sources.implementations.hashicorp_vault import SecretEngine
from radkit_service.webserver.models.base import DontUpdate, RADKitBaseModel, UpdateField
from typing_extensions import Literal

__all__ = ['UpdateExternalSource', 'StoredExternalSources', 'NewExternalSource', 'DeleteExternalSources', 'NewKeyboardInteractiveChallenge', 'NewCyberArkConjur', 'UpdateKeyboardInteractiveChallenge', 'UpdateCyberArkConjur', 'NewTacacsPlus', 'UpdateTacacsPlus', 'NewCyberArkAimCcp', 'UpdateCyberArkAimCcp', 'StoredHashiCorpVault', 'NewHashiCorpVault', 'UpdateHashiCorpVault', 'NewHashiCorpVaultTokenAuth', 'NewHashiCorpVaultAppRoleAuth', 'UpdateHashiCorpVaultTokenAuth', 'UpdateHashiCorpVaultAppRoleAuth']

class StoredKeyboardInteractiveChallenge(RADKitBaseModel):
    type: Literal[ExternalSourceType.KEYBOARD_INTERACTIVE_CHALLENGE]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: str
    @classmethod
    def from_db_obj(cls, db_obj: DbKeyboardInteractiveChallenge) -> StoredKeyboardInteractiveChallenge: ...

class NewKeyboardInteractiveChallenge(RADKitBaseModel):
    type: Literal[ExternalSourceType.KEYBOARD_INTERACTIVE_CHALLENGE]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: str
    password: CustomSecretStr
    privateKey: CustomSecretStr
    privateKeyPassword: CustomSecretStr
    def validate_private_key(cls, private_key: CustomSecretStr, info: ValidationInfo) -> CustomSecretStr: ...

class UpdateKeyboardInteractiveChallenge(RADKitBaseModel):
    type: Literal[ExternalSourceType.KEYBOARD_INTERACTIVE_CHALLENGE]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: UpdateField[str]
    password: UpdateField[AnnotatedCustomSecretStr]
    privateKey: UpdateField[AnnotatedCustomSecretStr]
    privateKeyPassword: CustomSecretStr
    def validate_private_key(cls, private_key: CustomSecretStr, info: ValidationInfo) -> CustomSecretStr: ...

class StoredCyberArkConjur(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_CONJUR]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    account: str
    username: str
    verify: bool
    useInsecureAlgorithms: bool
    @classmethod
    def from_db_obj(cls, db_obj: DbCyberArkConjur) -> StoredCyberArkConjur: ...

class NewCyberArkConjur(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_CONJUR]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    account: str
    username: str
    apiKey: CustomSecretStr
    verify: bool
    useInsecureAlgorithms: bool

class UpdateCyberArkConjur(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_CONJUR]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: UpdateField[AnyHttpUrl]
    account: UpdateField[str]
    username: UpdateField[str]
    apiKey: UpdateField[AnnotatedCustomSecretStr]
    verify: UpdateField[bool]
    useInsecureAlgorithms: UpdateField[bool]

class StoredTacacsPlus(RADKitBaseModel):
    type: Literal[ExternalSourceType.TACACS_PLUS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    host: str
    port: int
    @classmethod
    def from_db_obj(cls, db_obj: DbTacacsPlus) -> StoredTacacsPlus: ...
    @classmethod
    def validate_hostname(cls, hostname: str) -> str: ...

class NewTacacsPlus(RADKitBaseModel):
    type: Literal[ExternalSourceType.TACACS_PLUS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    host: str
    port: int
    secret: CustomSecretStr
    @classmethod
    def validate_port_in_range(cls, port: int) -> int: ...

class UpdateTacacsPlus(RADKitBaseModel):
    type: Literal[ExternalSourceType.TACACS_PLUS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    host: UpdateField[str]
    port: UpdateField[int]
    secret: UpdateField[AnnotatedCustomSecretStr]
    @classmethod
    def validate_port_in_range(cls, port: DontUpdate | int) -> DontUpdate | int: ...

class StoredCyberArkAimCpp(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_AIM_CCP]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    appId: str
    safe: str
    @classmethod
    def from_db_obj(cls, db_obj: DbCyberArkAimCcp) -> StoredCyberArkAimCpp: ...

class NewCyberArkAimCcp(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_AIM_CCP]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    appId: str
    safe: str
    certificate: CustomSecretStr
    def validate_certificate(cls, certificate: CustomSecretStr) -> CustomSecretStr: ...

class UpdateCyberArkAimCcp(RADKitBaseModel):
    type: Literal[ExternalSourceType.CYBERARK_AIM_CCP]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: UpdateField[AnyHttpUrl]
    appId: UpdateField[str]
    safe: UpdateField[str]
    certificate: UpdateField[AnnotatedCustomSecretStr]
    def validate_certificate(cls, certificate: UpdateField[AnnotatedCustomSecretStr]) -> UpdateField[AnnotatedCustomSecretStr]: ...

class NewStaticCredentials(RADKitBaseModel):
    type: Literal[ExternalSourceType.STATIC_CREDENTIALS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: str
    password: CustomSecretStr

class UpdateStaticCredentials(RADKitBaseModel):
    type: Literal[ExternalSourceType.STATIC_CREDENTIALS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: UpdateField[str]
    password: UpdateField[AnnotatedCustomSecretStr]

class StoredStaticCredentials(RADKitBaseModel):
    type: Literal[ExternalSourceType.STATIC_CREDENTIALS]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    username: str
    @classmethod
    def from_db_obj(cls, db_obj: DbStaticCredentials) -> StoredStaticCredentials: ...

class NewPlugin(RADKitBaseModel):
    type: Literal[ExternalSourceType.PLUGIN]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE, ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    pluginName: str
    @classmethod
    def check_existence_of_plugin(cls, plugin_name: str) -> str: ...
    @classmethod
    def from_db_obj(cls, db_obj: DbPlugin) -> NewPlugin: ...

class UpdatePlugin(RADKitBaseModel):
    type: Literal[ExternalSourceType.PLUGIN]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE, ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    pluginName: UpdateField[str]
    @classmethod
    def from_db_obj(cls, db_obj: DbPlugin) -> UpdatePlugin: ...

class StoredPlugin(RADKitBaseModel):
    type: Literal[ExternalSourceType.PLUGIN]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE, ExternalSourceAuthenticationType.ADMIN, ExternalSourceAuthenticationType.REMOTE_USER]]
    pluginName: str
    @classmethod
    def from_db_obj(cls, db_obj: DbPlugin) -> StoredPlugin: ...

class StoredHashiCorpVaultAuth(RADKitBaseModel):
    method: Literal['token', 'approle']
    path: str

class StoredHashiCorpVault(RADKitBaseModel):
    type: Literal[ExternalSourceType.HASHICORP_VAULT]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    engine: SecretEngine
    enginePath: str
    auth: StoredHashiCorpVaultAuth
    verify: bool
    useInsecureAlgorithms: bool
    @classmethod
    def from_db_obj(cls, db_obj: DbHashiCorpVault) -> StoredHashiCorpVault: ...

class NewHashiCorpVaultTokenAuth(RADKitBaseModel):
    method: Literal['token']
    path: str
    token: CustomSecretStr

class NewHashiCorpVaultAppRoleAuth(RADKitBaseModel):
    method: Literal['approle']
    path: str
    roleId: CustomSecretStr
    secretId: CustomSecretStr

class NewHashiCorpVault(RADKitBaseModel):
    type: Literal[ExternalSourceType.HASHICORP_VAULT]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: AnyHttpUrl
    engine: SecretEngine
    enginePath: str
    auth: NewHashiCorpVaultTokenAuth | NewHashiCorpVaultAppRoleAuth
    verify: bool
    useInsecureAlgorithms: bool

class UpdateHashiCorpVaultTokenAuth(RADKitBaseModel):
    method: Literal['token']
    path: str
    token: UpdateField[AnnotatedCustomSecretStr]

class UpdateHashiCorpVaultAppRoleAuth(RADKitBaseModel):
    method: Literal['approle']
    path: str
    roleId: UpdateField[AnnotatedCustomSecretStr]
    secretId: UpdateField[AnnotatedCustomSecretStr]

class UpdateHashiCorpVault(RADKitBaseModel):
    type: Literal[ExternalSourceType.HASHICORP_VAULT]
    authentication_types: set[Literal[ExternalSourceAuthenticationType.DEVICE]]
    baseUrl: UpdateField[AnyHttpUrl]
    engine: UpdateField[SecretEngine]
    enginePath: UpdateField[str]
    auth: UpdateField[UpdateHashiCorpVaultTokenAuth | UpdateHashiCorpVaultAppRoleAuth]
    verify: UpdateField[bool]
    useInsecureAlgorithms: UpdateField[bool]

class StoredExternalSources(RADKitBaseModel):
    name: str
    options: StoredKeyboardInteractiveChallenge | StoredCyberArkConjur | StoredCyberArkAimCpp | StoredTacacsPlus | StoredStaticCredentials | StoredPlugin | StoredHashiCorpVault
    @classmethod
    def from_db_external_sources(cls, external_source: DbExternalSource) -> StoredExternalSources: ...

class NewExternalSource(RADKitBaseModel):
    name: str
    options: NewKeyboardInteractiveChallenge | NewCyberArkConjur | NewCyberArkAimCcp | NewTacacsPlus | NewStaticCredentials | NewPlugin | NewHashiCorpVault

class UpdateExternalSource(RADKitBaseModel):
    name: str
    options: UpdateKeyboardInteractiveChallenge | UpdateCyberArkConjur | UpdateCyberArkAimCcp | UpdateTacacsPlus | UpdateStaticCredentials | UpdatePlugin | UpdateHashiCorpVault

class DeleteExternalSources(RADKitRootModel[list[str]]):
    root: list[str]
    model_config: Incomplete
