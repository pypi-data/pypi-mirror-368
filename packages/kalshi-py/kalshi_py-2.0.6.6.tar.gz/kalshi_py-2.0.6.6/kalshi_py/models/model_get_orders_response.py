from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_order import ModelOrder


T = TypeVar("T", bound="ModelGetOrdersResponse")


@_attrs_define
class ModelGetOrdersResponse:
    """
    Attributes:
        cursor (Union[Unset, str]): The Cursor represents a pointer to the next page of records in the pagination. Use
            the value returned here in the cursor query parameter for this end-point to get the next page containing limit
            records. An empty value of this field indicates there is no next page.
        orders (Union[Unset, list['ModelOrder']]):
    """

    cursor: Union[Unset, str] = UNSET
    orders: Union[Unset, list["ModelOrder"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cursor = self.cursor

        orders: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.orders, Unset):
            orders = []
            for componentsschemasmodel_order_list_item_data in self.orders:
                componentsschemasmodel_order_list_item = componentsschemasmodel_order_list_item_data.to_dict()
                orders.append(componentsschemasmodel_order_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cursor is not UNSET:
            field_dict["cursor"] = cursor
        if orders is not UNSET:
            field_dict["orders"] = orders

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_order import ModelOrder

        d = dict(src_dict)
        cursor = d.pop("cursor", UNSET)

        orders = []
        _orders = d.pop("orders", UNSET)
        for componentsschemasmodel_order_list_item_data in _orders or []:
            componentsschemasmodel_order_list_item = ModelOrder.from_dict(componentsschemasmodel_order_list_item_data)

            orders.append(componentsschemasmodel_order_list_item)

        model_get_orders_response = cls(
            cursor=cursor,
            orders=orders,
        )

        model_get_orders_response.additional_properties = d
        return model_get_orders_response

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
