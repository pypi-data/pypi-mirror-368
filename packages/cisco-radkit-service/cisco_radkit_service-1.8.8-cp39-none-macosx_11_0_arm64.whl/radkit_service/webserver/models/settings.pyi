from pydantic import BaseModel
from radkit_common.settings import SettingChangeParam, SettingInfo
from typing import Annotated, Any
from typing_extensions import Literal

__all__ = ['SettingChange']

class SettingChange(BaseModel):
    setting: str
    layers: list[Literal['toml', 'api']]
    value: Any
    remove: bool
    def to_setting_change_param(self) -> SettingChangeParam: ...

class APISettingInfo(BaseModel):
    setting: str
    effective_value: Annotated[Any, None]
    type: str
    value_source: Literal['default', 'toml', 'env', 'cli', 'api']
    description: str
    api_writable: bool
    api_persistent: bool
    webui_visible: bool
    layer_values: dict[Literal['default', 'toml', 'env', 'cli', 'api'], Annotated[Any, None]]
    layer_errors: dict[Literal['default', 'toml', 'env', 'cli', 'api'], str]
    @classmethod
    def from_setting_info(cls, setting_info: SettingInfo) -> APISettingInfo: ...
