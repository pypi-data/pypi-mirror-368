from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_stock import BatchStock
from ...models.batch_stock_update import BatchStockUpdate
from ...models.detailed_error_response import DetailedErrorResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    batch_id: int,
    *,
    body: BatchStockUpdate,
    location_id: Unset | int = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["location_id"] = location_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/batch_stocks/{batch_id}",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BatchStock | DetailedErrorResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = BatchStock.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 422:
        response_422 = DetailedErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BatchStock | DetailedErrorResponse | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    batch_id: int,
    *,
    client: AuthenticatedClient | Client,
    body: BatchStockUpdate,
    location_id: Unset | int = UNSET,
) -> Response[BatchStock | DetailedErrorResponse | ErrorResponse]:
    """Update batch details

     Updates the specified batch details by setting the values of the parameters passed. Any parameters
    not provided will be left unchanged.

    Args:
        batch_id (int):
        location_id (Union[Unset, int]):
        body (BatchStockUpdate):  Example: {'batch_number': 'BAT-1', 'expiration_date':
            '2020-10-23T10:37:05.085Z', 'batch_created_date': '2020-10-23T10:37:05.085Z',
            'batch_barcode': '0040'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[BatchStock, DetailedErrorResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        batch_id=batch_id,
        body=body,
        location_id=location_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    batch_id: int,
    *,
    client: AuthenticatedClient | Client,
    body: BatchStockUpdate,
    location_id: Unset | int = UNSET,
) -> BatchStock | DetailedErrorResponse | ErrorResponse | None:
    """Update batch details

     Updates the specified batch details by setting the values of the parameters passed. Any parameters
    not provided will be left unchanged.

    Args:
        batch_id (int):
        location_id (Union[Unset, int]):
        body (BatchStockUpdate):  Example: {'batch_number': 'BAT-1', 'expiration_date':
            '2020-10-23T10:37:05.085Z', 'batch_created_date': '2020-10-23T10:37:05.085Z',
            'batch_barcode': '0040'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[BatchStock, DetailedErrorResponse, ErrorResponse]
    """

    return sync_detailed(
        batch_id=batch_id,
        client=client,
        body=body,
        location_id=location_id,
    ).parsed


async def asyncio_detailed(
    batch_id: int,
    *,
    client: AuthenticatedClient | Client,
    body: BatchStockUpdate,
    location_id: Unset | int = UNSET,
) -> Response[BatchStock | DetailedErrorResponse | ErrorResponse]:
    """Update batch details

     Updates the specified batch details by setting the values of the parameters passed. Any parameters
    not provided will be left unchanged.

    Args:
        batch_id (int):
        location_id (Union[Unset, int]):
        body (BatchStockUpdate):  Example: {'batch_number': 'BAT-1', 'expiration_date':
            '2020-10-23T10:37:05.085Z', 'batch_created_date': '2020-10-23T10:37:05.085Z',
            'batch_barcode': '0040'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[BatchStock, DetailedErrorResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        batch_id=batch_id,
        body=body,
        location_id=location_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    batch_id: int,
    *,
    client: AuthenticatedClient | Client,
    body: BatchStockUpdate,
    location_id: Unset | int = UNSET,
) -> BatchStock | DetailedErrorResponse | ErrorResponse | None:
    """Update batch details

     Updates the specified batch details by setting the values of the parameters passed. Any parameters
    not provided will be left unchanged.

    Args:
        batch_id (int):
        location_id (Union[Unset, int]):
        body (BatchStockUpdate):  Example: {'batch_number': 'BAT-1', 'expiration_date':
            '2020-10-23T10:37:05.085Z', 'batch_created_date': '2020-10-23T10:37:05.085Z',
            'batch_barcode': '0040'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[BatchStock, DetailedErrorResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            batch_id=batch_id,
            client=client,
            body=body,
            location_id=location_id,
        )
    ).parsed
