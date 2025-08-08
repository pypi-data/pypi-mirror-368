from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pydantic import BaseModel
from radkit_common.terminal_interaction.provisioning_variants import ProvisioningVariant
from radkit_common.types import ConnectionMethod, HTTPProtocol, TerminalCapabilities
from radkit_service.terminal_interaction.ssh import KeyboardInteractiveAuthRequestCb, KeyboardInteractiveChallengeReceivedCb
from typing import Literal, TypedDict

__all__ = ['SSHClientParameters', 'TerminalConnectionParameters', 'NetconfConnectionParameters', 'SwaggerConnectionParameters', 'SwaggerConnectionParameters', 'SNMPConnectionParameters', 'HTTPConnectionParameters', 'AuthenticatedUser', 'AuthorizedUser', 'ExternalSourceSecret', 'ExternalSourceValue']

class SSHClientParameters(TypedDict):
    keyboard_interactive_auth_requested_cb: KeyboardInteractiveAuthRequestCb | None
    keyboard_interactive_challenge_received_cb: KeyboardInteractiveChallengeReceivedCb | None

class TerminalConnectionParameters(TypedDict):
    username: str
    password: str
    port: int
    connection_method: ConnectionMethod | str
    enable_password: str
    enable_set: bool
    use_insecure_algorithms: bool
    private_key: str
    use_tunneling_if_jumphost: bool
    ssh_client_parameters: SSHClientParameters | None
    provisioning_variant: ProvisioningVariant | str
    capabilities: Collection[TerminalCapabilities | str]

class NetconfConnectionParameters(TypedDict):
    username: str
    password: str
    port: int
    use_insecure_algorithms: bool

class SwaggerConnectionParameters(TypedDict):
    username: str
    password: str
    verify: bool
    use_insecure_algorithms: bool
    schema_path: str
    port: int

class SNMPConnectionParameters(TypedDict):
    version: int
    community_string: str
    port: int

class HTTPConnectionParameters(TypedDict):
    username: str
    password: str
    port: int
    protocol: HTTPProtocol | str
    verify: bool
    use_insecure_algorithms: bool
    authentication_extra: str | None

class AuthenticatedUser(TypedDict):
    username: str
    email: str
    fullname: str
    description: str

@dataclass
class ExternalSourceSecret:
    external_source: str
    path: str

@dataclass
class ExternalSourceValue:
    value: str

@dataclass
class ExternalSourceReference:
    name: str
    params: Mapping[str, str]

@dataclass
class ExternalSourceTerminal:
    external_source: ExternalSourceReference | None
    port: int
    connection_method: Literal[ConnectionMethod.SSH, ConnectionMethod.TELNET, ConnectionMethod.SSHPUBKEY, ConnectionMethod.TELNET_NO_AUTH]
    use_insecure_algorithms: bool
    use_tunneling_if_jumphost: bool
    provisioning_variant: ProvisioningVariant
    capabilities: frozenset[TerminalCapabilities]
    username: ExternalSourceSecret | ExternalSourceValue | None
    password: ExternalSourceSecret | None
    enable_password: ExternalSourceSecret | None
    private_key: ExternalSourceSecret | None

@dataclass
class ExternalSourceNetconf:
    external_source: ExternalSourceReference | None
    port: int
    use_insecure_algorithms: bool
    username: ExternalSourceSecret | ExternalSourceValue | None
    password: ExternalSourceSecret | None

@dataclass
class ExternalSourceSnmp:
    external_source: ExternalSourceReference | None
    version: int
    port: int
    community_string: ExternalSourceSecret | None

@dataclass
class ExternalSourceSwagger:
    external_source: ExternalSourceReference | None
    port: int
    schema_path: str
    verify: bool
    use_insecure_algorithms: bool
    username: ExternalSourceSecret | ExternalSourceValue | None
    password: ExternalSourceSecret | None

@dataclass
class ExternalSourceHttp:
    external_source: ExternalSourceReference | None
    port: int
    protocol: HTTPProtocol
    verify: bool
    use_insecure_algorithms: bool
    authentication_extra: str | None
    username: ExternalSourceSecret | ExternalSourceValue | None
    password: ExternalSourceSecret | None

class AuthorizedUser(TypedDict):
    connection_mode_cloud_active: bool
    connection_mode_direct_active: bool
    connection_mode_direct_sso_active: bool

class ProtocolsDefinition(BaseModel):
    terminal: ExternalSourceTerminal | None
    netconf: ExternalSourceNetconf | None
    snmp: ExternalSourceSnmp | None
    swagger: ExternalSourceSwagger | None
    http: ExternalSourceHttp | None
