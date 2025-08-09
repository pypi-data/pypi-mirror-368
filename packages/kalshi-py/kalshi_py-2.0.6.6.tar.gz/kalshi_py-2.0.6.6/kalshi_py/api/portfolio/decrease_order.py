from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.model_decrease_order_request import ModelDecreaseOrderRequest
from ...models.model_decrease_order_response import ModelDecreaseOrderResponse
from ...types import Response


def _get_kwargs(
    order_id: str,
    *,
    body: ModelDecreaseOrderRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/portfolio/orders/{order_id}/decrease",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ModelDecreaseOrderResponse]:
    if response.status_code == 200:
        response_200 = ModelDecreaseOrderResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ModelDecreaseOrderResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    order_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelDecreaseOrderRequest,
) -> Response[ModelDecreaseOrderResponse]:
    """Decrease Order

      Endpoint for decreasing the number of contracts in an existing order. This is the only kind of edit
    available on order quantity. Cancelling an order is equivalent to decreasing an order amount to
    zero.

    Args:
        order_id (str): Order ID
        body (ModelDecreaseOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModelDecreaseOrderResponse]
    """

    kwargs = _get_kwargs(
        order_id=order_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    order_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelDecreaseOrderRequest,
) -> Optional[ModelDecreaseOrderResponse]:
    """Decrease Order

      Endpoint for decreasing the number of contracts in an existing order. This is the only kind of edit
    available on order quantity. Cancelling an order is equivalent to decreasing an order amount to
    zero.

    Args:
        order_id (str): Order ID
        body (ModelDecreaseOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ModelDecreaseOrderResponse
    """

    return sync_detailed(
        order_id=order_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    order_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelDecreaseOrderRequest,
) -> Response[ModelDecreaseOrderResponse]:
    """Decrease Order

      Endpoint for decreasing the number of contracts in an existing order. This is the only kind of edit
    available on order quantity. Cancelling an order is equivalent to decreasing an order amount to
    zero.

    Args:
        order_id (str): Order ID
        body (ModelDecreaseOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModelDecreaseOrderResponse]
    """

    kwargs = _get_kwargs(
        order_id=order_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    order_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelDecreaseOrderRequest,
) -> Optional[ModelDecreaseOrderResponse]:
    """Decrease Order

      Endpoint for decreasing the number of contracts in an existing order. This is the only kind of edit
    available on order quantity. Cancelling an order is equivalent to decreasing an order amount to
    zero.

    Args:
        order_id (str): Order ID
        body (ModelDecreaseOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ModelDecreaseOrderResponse
    """

    return (
        await asyncio_detailed(
            order_id=order_id,
            client=client,
            body=body,
        )
    ).parsed
