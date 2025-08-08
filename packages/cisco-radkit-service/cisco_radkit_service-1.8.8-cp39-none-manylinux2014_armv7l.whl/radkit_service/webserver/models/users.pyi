from .base import RADKitBaseModel, RADKitRootModel, UpdateField, UpdateModel
from .labels import UpdateLabelSet
from _typeshed import Incomplete
from collections.abc import Sequence, Set
from pydantic import AwareDatetime, EmailStr, PositiveInt
from radkit_common.types import AnnotatedCustomSecretStr, CustomSecretStr
from radkit_service.database import DbAdmin, DbRemoteUser, ServiceDB
from radkit_service.database.models import DbRemoteUserExternalAuth
from typing import Annotated, Literal

__all__ = ['StoredRemoteUser', 'NewRemoteUser', 'NewRemoteUsers', 'UpdateRemoteUser', 'UpdateRemoteUsers', 'DeleteRemoteUsers', 'NewExternalAuth', 'NewAdmin', 'NewAdmins', 'UpdateAdmin', 'UpdateAdmins', 'ChangeAdminPassword', 'NewLoginAttempt']

class StoredExternalAuth(RADKitBaseModel):
    externalSource: str
    externalUsername: str | None
    @classmethod
    def from_db_external_auth(cls, db_external_auth: DbRemoteUserExternalAuth | None) -> StoredExternalAuth | None: ...

class StoredRemoteUser(RADKitBaseModel):
    username: str
    fullname: str
    description: str
    timeSliceMinutes: PositiveInt | None
    expirationTimestamp: AwareDatetime | None
    labels: Set[int]
    accessToken: AnnotatedCustomSecretStr
    connectionModeCloudActive: bool
    connectionModeDirectActive: bool
    connectionModeDirectSsoActive: bool
    externalAuth: StoredExternalAuth | None
    @classmethod
    def from_db_user(cls, db: ServiceDB, user: DbRemoteUser) -> StoredRemoteUser: ...

class NewExternalAuth(StoredExternalAuth): ...

class NewRemoteUser(RADKitBaseModel):
    username: EmailStr
    fullname: str
    description: str
    timeSliceMinutes: PositiveInt | None
    expirationTimestamp: Annotated[AwareDatetime | None, None]
    labels: Sequence[int | str]
    accessToken: CustomSecretStr | None
    connectionModeCloudActive: bool
    connectionModeDirectActive: bool
    connectionModeDirectSsoActive: bool
    externalAuth: NewExternalAuth | None
    @classmethod
    def validate_access_token(cls, v: CustomSecretStr | None) -> CustomSecretStr | None: ...

class NewRemoteUsers(RADKitRootModel[list[NewRemoteUser]]):
    root: list[NewRemoteUser]
    model_config: Incomplete

class UpdateExternalAuth(UpdateModel):
    externalSource: UpdateField[str]
    externalUsername: UpdateField[str | None]

class UpdateRemoteUser(RADKitBaseModel):
    username: EmailStr
    newUsername: UpdateField[EmailStr]
    fullname: UpdateField[str]
    description: UpdateField[str]
    expirationTimestamp: UpdateField[Annotated[AwareDatetime | None, None] | None]
    timeSliceMinutes: UpdateField[PositiveInt | None]
    labelUpdate: UpdateLabelSet
    accessToken: UpdateField[AnnotatedCustomSecretStr]
    connectionModeCloudActive: UpdateField[bool]
    connectionModeDirectActive: UpdateField[bool]
    connectionModeDirectSsoActive: UpdateField[bool]
    externalAuth: UpdateField[UpdateExternalAuth | None]
    @classmethod
    def validate_access_token(cls, value: UpdateField[AnnotatedCustomSecretStr]) -> UpdateField[AnnotatedCustomSecretStr]: ...

class UpdateRemoteUsers(RADKitRootModel[list[UpdateRemoteUser]]):
    root: list[UpdateRemoteUser]
    model_config: Incomplete

class DeleteRemoteUsers(RADKitRootModel[list[str]]):
    root: list[str]
    model_config: Incomplete

class StoredAdmin(RADKitBaseModel):
    username: str
    email: Literal[''] | EmailStr
    fullname: str
    description: str
    enabled: bool
    external_source_ref: str | None
    @classmethod
    def from_db_admin(cls, user: DbAdmin) -> StoredAdmin: ...

class NewAdmin(RADKitBaseModel):
    username: str
    email: Literal[''] | EmailStr
    fullname: str
    description: str
    password: CustomSecretStr
    enabled: bool
    def dump_secret(self, v: CustomSecretStr) -> str: ...
    @classmethod
    def validate_username(cls, v: str) -> str: ...
    @classmethod
    def validate_password(cls, v: CustomSecretStr) -> CustomSecretStr: ...

class NewAdmins(RADKitRootModel[list[NewAdmin]]):
    root: list[NewAdmin]
    model_config: Incomplete

class UpdateAdmin(RADKitBaseModel):
    username: str
    enabled: UpdateField[bool]
    email: UpdateField[Literal[''] | EmailStr]
    fullname: UpdateField[str]
    description: UpdateField[str]

class UpdateAdmins(RADKitRootModel[list[UpdateAdmin]]):
    root: list[UpdateAdmin]
    model_config: Incomplete

class ChangeAdminPassword(RADKitBaseModel):
    oldPassword: CustomSecretStr | None
    password: CustomSecretStr
    username: str | None
    def dump_secret(self, v: CustomSecretStr) -> str: ...
    @classmethod
    def validate_password(cls, v: CustomSecretStr) -> CustomSecretStr: ...

class DeleteAdmins(RADKitRootModel[list[str]]):
    root: list[str]
    model_config: Incomplete

class NewLoginAttempt(RADKitBaseModel):
    succeeded: bool
    attempt_time: AwareDatetime
    ip_address: str
    user_agent: str
