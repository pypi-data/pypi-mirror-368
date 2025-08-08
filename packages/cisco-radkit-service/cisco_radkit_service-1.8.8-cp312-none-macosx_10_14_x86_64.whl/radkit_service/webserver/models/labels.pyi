from .base import RADKitBaseModel, RADKitRootModel, UpdateField
from collections.abc import Sequence
from radkit_service.database import DbLabel
from typing import Any

__all__ = ['StoredLabel', 'NewLabel', 'NewLabels', 'UpdateLabel', 'UpdateLabels', 'DeleteLabels']

class StoredLabel(RADKitBaseModel):
    id: int
    name: str
    color: str
    @classmethod
    def from_db_label(cls, label: DbLabel) -> StoredLabel: ...

class NewLabel(RADKitBaseModel):
    name: str
    color: str

class NewLabels(RADKitRootModel[list[NewLabel]]):
    root: list[NewLabel]

class UpdateLabel(RADKitBaseModel):
    id: int
    name: UpdateField[NonEmptyLabel]
    color: UpdateField[str]

class UpdateLabels(RADKitRootModel[list[UpdateLabel]]):
    root: list[UpdateLabel]

class DeleteLabels(RADKitRootModel[list[int]]):
    root: list[int]

class UpdateLabelSet(RADKitBaseModel):
    replace: Sequence[int | str] | None
    add: Sequence[int | str]
    remove: Sequence[int | str]
    @classmethod
    def check_labels_replace_xor_add_remove(cls, values: dict[str, Any]) -> dict[str, Any]: ...
