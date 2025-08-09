from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelGetUserRestingOrderTotalValueResponse")


@_attrs_define
class ModelGetUserRestingOrderTotalValueResponse:
    """
    Attributes:
        total_value (Union[Unset, int]):
    """

    total_value: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_value = self.total_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_value is not UNSET:
            field_dict["total_value"] = total_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_value = d.pop("total_value", UNSET)

        model_get_user_resting_order_total_value_response = cls(
            total_value=total_value,
        )

        model_get_user_resting_order_total_value_response.additional_properties = d
        return model_get_user_resting_order_total_value_response

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
