from pydantic import BaseModel
from radkit_common.identities import ServiceID
from radkit_service.launcher import ServiceState

__all__ = ['Status']

class CloudStatus(BaseModel):
    domain: str
    base_url: str | None
    enrolled: bool
    service_id: ServiceID | None
    connected: bool
    connected_message: str

class Status(BaseModel):
    version: str
    username: str | None
    bootstrapped: bool
    cloud_rpc_enabled: bool
    direct_rpc_enabled: bool
    direct_rpc_port: int | None
    cloud: CloudStatus | None
    e2ee_sha256_fingerprint: str | None
    webserver_sha256_fingerprint: str | None
    @classmethod
    def for_bootstrap(cls) -> Status: ...
    @classmethod
    async def from_service_state(cls, service_state: ServiceState, username: str) -> Status: ...
