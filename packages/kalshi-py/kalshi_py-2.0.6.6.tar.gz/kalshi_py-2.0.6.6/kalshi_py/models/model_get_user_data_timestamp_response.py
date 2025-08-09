from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelGetUserDataTimestampResponse")


@_attrs_define
class ModelGetUserDataTimestampResponse:
    """
    Attributes:
        as_of_time (Union[Unset, Any]):
    """

    as_of_time: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        as_of_time = self.as_of_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if as_of_time is not UNSET:
            field_dict["as_of_time"] = as_of_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        as_of_time = d.pop("as_of_time", UNSET)

        model_get_user_data_timestamp_response = cls(
            as_of_time=as_of_time,
        )

        model_get_user_data_timestamp_response.additional_properties = d
        return model_get_user_data_timestamp_response

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
