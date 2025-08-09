from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_structured_target import ModelStructuredTarget


T = TypeVar("T", bound="ModelGetStructuredTargetResponse")


@_attrs_define
class ModelGetStructuredTargetResponse:
    """
    Attributes:
        structured_target (Union[Unset, ModelStructuredTarget]):
    """

    structured_target: Union[Unset, "ModelStructuredTarget"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        structured_target: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.structured_target, Unset):
            structured_target = self.structured_target.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if structured_target is not UNSET:
            field_dict["structured_target"] = structured_target

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_structured_target import ModelStructuredTarget

        d = dict(src_dict)
        _structured_target = d.pop("structured_target", UNSET)
        structured_target: Union[Unset, ModelStructuredTarget]
        if isinstance(_structured_target, Unset):
            structured_target = UNSET
        else:
            structured_target = ModelStructuredTarget.from_dict(_structured_target)

        model_get_structured_target_response = cls(
            structured_target=structured_target,
        )

        model_get_structured_target_response.additional_properties = d
        return model_get_structured_target_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
