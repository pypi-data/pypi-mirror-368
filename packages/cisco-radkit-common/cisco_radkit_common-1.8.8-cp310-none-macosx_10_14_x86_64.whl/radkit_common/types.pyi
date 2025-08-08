import aiohttp
from .settings import BaseProxySettings
from _typeshed import Incomplete
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, GetCoreSchemaHandler, SecretStr, model_serializer
from typing import Any
from typing_extensions import TypeAlias

__all__ = ['AnnotatedCustomSecretStr', 'CustomSecretStr', 'PossiblyEncryptedStr', 'PlainSecretOrSecretFromVault', 'NoProxy', 'NoneType', 'Proxy', 'ProxyInfo', 'PortRanges', 'ConnectionMethod', 'DeviceType', 'HTTPProtocol', 'UIDeviceType', 'ExternalSourceAuthenticationType', 'UI_EXTERNAL_SOURCE_TYPE', 'SecretFromVault', 'PlainSecret', 'TerminalCapabilities', 'OAuthProvider', 'JTI', 'JWTIssuer', 'DEPRECATED_DEVICE_TYPE_NAMES']

NoneType: Incomplete

class CustomSecretStr(SecretStr):
    PLACEHOLDER: str

AnnotatedCustomSecretStr: Incomplete

class SecretFromVault(BaseModel):
    from_vault: str
    @model_serializer
    def serialize_model(self) -> SecretFromVaultSerializedTuple: ...

class PlainSecret(CustomSecretStr):
    def __eq__(self, other: object) -> bool: ...
PlainSecretOrSecretFromVault = PlainSecret | SecretFromVault
PossiblyEncryptedStr: Incomplete

@dataclass(frozen=True)
class NoProxy:
    url: None = ...
    username: None = ...
    password: None = ...
    def get_aiohttp_basic_auth(self) -> None: ...
    def get_httpx_proxy(self) -> None: ...

@dataclass(frozen=True)
class Proxy:
    url: str
    username: str = ...
    password: CustomSecretStr = ...
    @classmethod
    def from_settings(cls, settings: BaseProxySettings) -> Proxy: ...
    def get_aiohttp_basic_auth(self) -> aiohttp.BasicAuth | None: ...
    def get_httpx_proxy(self) -> str: ...
ProxyInfo: TypeAlias = NoProxy | Proxy

class PortRanges(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> object: ...
    @classmethod
    def validate(cls, value: str, info: Any) -> _T: ...
    def is_port_valid(self, port: int) -> bool: ...

class ConnectionMethod(str, Enum):
    SSH = 'SSH'
    SSHPUBKEY = 'SSHPUBKEY'
    TELNET = 'TELNET'
    TELNET_NO_AUTH = 'TELNET_NO_AUTH'
    NETCONF = 'NETCONF'

class DeviceType(str, Enum):
    AIRE_OS = 'AIRE_OS'
    APIC = 'APIC'
    ASA = 'ASA'
    BROADWORKS = 'BROADWORKS'
    CATALYST_CENTER = 'CATALYST_CENTER'
    CEDGE = 'CEDGE'
    CIMC = 'CIMC'
    CISCO_AP_OS = 'CISCO_AP_OS'
    CML = 'CML'
    CMS = 'CMS'
    CPS = 'CPS'
    CROSSWORK = 'CROSSWORK'
    CSPC = 'CSPC'
    CUCM = 'CUCM'
    CVOS = 'CVOS'
    CVP = 'CVP'
    ESA = 'ESA'
    EXPRESSWAY = 'EXPRESSWAY'
    FDM = 'FDM'
    FMC = 'FMC'
    FTD = 'FTD'
    GENERIC = 'GENERIC'
    HYPERFLEX = 'HYPERFLEX'
    INTERSIGHT = 'INTERSIGHT'
    IOS_XE = 'IOS_XE'
    IOS_XR = 'IOS_XR'
    ISE = 'ISE'
    LINUX = 'LINUX'
    NCS_2000 = 'NCS_2000'
    NEXUS_DASHBOARD = 'NEXUS_DASHBOARD'
    NSO = 'NSO'
    NX_OS = 'NX_OS'
    RADKIT_SERVICE = 'RADKIT_SERVICE'
    ROUTED_PON = 'ROUTED_PON'
    SMA = 'SMA'
    SPLUNK = 'SPLUNK'
    STAR_OS = 'STAR_OS'
    UCCE = 'UCCE'
    UCS_MANAGER = 'UCS_MANAGER'
    ULTRA_CORE_5G_AMF = 'ULTRA_CORE_5G_AMF'
    ULTRA_CORE_5G_PCF = 'ULTRA_CORE_5G_PCF'
    ULTRA_CORE_5G_SMF = 'ULTRA_CORE_5G_SMF'
    WAS = 'WAS'
    WLC = 'WLC'
    VMANAGE = 'VMANAGE'

DEPRECATED_DEVICE_TYPE_NAMES: Incomplete
UIDeviceType: dict[DeviceType, str]

class TerminalCapabilities(str, Enum):
    INTERACTIVE = 'INTERACTIVE'
    EXEC = 'EXEC'
    UPLOAD = 'UPLOAD'
    DOWNLOAD = 'DOWNLOAD'

class HTTPProtocol(str, Enum):
    HTTP = 'HTTP'
    HTTPS = 'HTTPS'

class ExternalSourceAuthenticationType(str, Enum):
    DEVICE = 'DEVICE'
    ADMIN = 'ADMIN'
    REMOTE_USER = 'REMOTE-USER'

class ExternalSourceType(str, Enum):
    KEYBOARD_INTERACTIVE_CHALLENGE = 'KEYBOARD_INTERACTIVE_CHALLENGE'
    CYBERARK_CONJUR = 'CYBERARK_CONJUR'
    CYBERARK_AIM_CCP = 'CYBERARK_AIM_CCP'
    STATIC_CREDENTIALS = 'STATIC_CREDENTIALS'
    PLUGIN = 'PLUGIN'
    HASHICORP_VAULT = 'HASHICORP_VAULT'
    TACACS_PLUS = 'TACACS_PLUS'

UI_EXTERNAL_SOURCE_TYPE: Mapping[ExternalSourceType, str]
OAuthProvider: Incomplete
JWTIssuer: Incomplete
JTI: Incomplete
