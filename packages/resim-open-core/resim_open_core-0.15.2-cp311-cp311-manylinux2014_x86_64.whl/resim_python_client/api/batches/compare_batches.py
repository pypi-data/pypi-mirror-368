from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import Dict
from typing import Union
from ...models.compare_batches_output import CompareBatchesOutput
from typing import cast
from ...models.compare_batches_status_filter import CompareBatchesStatusFilter
from ...types import UNSET, Unset



def _get_kwargs(
    project_id: str,
    batch_id: str,
    other_batch_id: str,
    *,
    status: Union[Unset, CompareBatchesStatusFilter] = UNSET,
    search: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["search"] = search

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/batches/{batch_id}/compare/{other_batch_id}".format(project_id=project_id,batch_id=batch_id,other_batch_id=other_batch_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, CompareBatchesOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CompareBatchesOutput.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, CompareBatchesOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    other_batch_id: str,
    *,
    client: AuthenticatedClient,
    status: Union[Unset, CompareBatchesStatusFilter] = UNSET,
    search: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, CompareBatchesOutput]]:
    """  Get a summary describing how individual tests have changed between the two given batches. A warning
    or a blocking failure is considered failing from the point of view of filters and ordering.

    Args:
        project_id (str):
        batch_id (str):
        other_batch_id (str):
        status (Union[Unset, CompareBatchesStatusFilter]):
        search (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CompareBatchesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
other_batch_id=other_batch_id,
status=status,
search=search,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    batch_id: str,
    other_batch_id: str,
    *,
    client: AuthenticatedClient,
    status: Union[Unset, CompareBatchesStatusFilter] = UNSET,
    search: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, CompareBatchesOutput]]:
    """  Get a summary describing how individual tests have changed between the two given batches. A warning
    or a blocking failure is considered failing from the point of view of filters and ordering.

    Args:
        project_id (str):
        batch_id (str):
        other_batch_id (str):
        status (Union[Unset, CompareBatchesStatusFilter]):
        search (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CompareBatchesOutput]
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
other_batch_id=other_batch_id,
client=client,
status=status,
search=search,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    other_batch_id: str,
    *,
    client: AuthenticatedClient,
    status: Union[Unset, CompareBatchesStatusFilter] = UNSET,
    search: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, CompareBatchesOutput]]:
    """  Get a summary describing how individual tests have changed between the two given batches. A warning
    or a blocking failure is considered failing from the point of view of filters and ordering.

    Args:
        project_id (str):
        batch_id (str):
        other_batch_id (str):
        status (Union[Unset, CompareBatchesStatusFilter]):
        search (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, CompareBatchesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
other_batch_id=other_batch_id,
status=status,
search=search,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    batch_id: str,
    other_batch_id: str,
    *,
    client: AuthenticatedClient,
    status: Union[Unset, CompareBatchesStatusFilter] = UNSET,
    search: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, CompareBatchesOutput]]:
    """  Get a summary describing how individual tests have changed between the two given batches. A warning
    or a blocking failure is considered failing from the point of view of filters and ordering.

    Args:
        project_id (str):
        batch_id (str):
        other_batch_id (str):
        status (Union[Unset, CompareBatchesStatusFilter]):
        search (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, CompareBatchesOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
other_batch_id=other_batch_id,
client=client,
status=status,
search=search,
page_size=page_size,
page_token=page_token,

    )).parsed
