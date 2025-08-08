from .status import Status
from _typeshed import Incomplete
from pydantic import AwareDatetime, BaseModel
from radkit_common.rpc import RPCName
from radkit_common.support_package import BasicSupportPackage

__all__ = ['OngoingRpcRequest', 'RpcSummary', 'ServiceSupportPackage']

class OngoingRpcRequest(BaseModel):
    rpcName: RPCName
    rpcSource: str
    uniqueRequestId: list[str]

class RpcSummary(BaseModel):
    activeRequestCount: int
    totalRequestCount: int
    ongoingRpcRequests: list[OngoingRpcRequest]

class ServiceSupportPackage(BaseModel):
    model_config: Incomplete
    basic_support_package: BasicSupportPackage
    service_started_at: AwareDatetime
    service_status: Status
    rpc_summary: RpcSummary | None
