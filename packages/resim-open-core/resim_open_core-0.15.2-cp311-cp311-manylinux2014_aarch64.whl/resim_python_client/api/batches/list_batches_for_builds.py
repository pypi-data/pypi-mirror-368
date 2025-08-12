from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import Dict
from typing import Union
from typing import cast
from typing import cast, List
from ...types import UNSET, Unset
from ...models.list_batches_output import ListBatchesOutput



def _get_kwargs(
    project_id: str,
    branch_id: str,
    build_id: List[str],
    *,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/branches/{branch_id}/builds/{build_id}/batches".format(project_id=project_id,branch_id=branch_id,build_id=build_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListBatchesOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListBatchesOutput.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListBatchesOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    branch_id: str,
    build_id: List[str],
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListBatchesOutput]]:
    """  Returns the batches for a build.

    Args:
        project_id (str):
        branch_id (str):
        build_id (List[str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListBatchesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
branch_id=branch_id,
build_id=build_id,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    branch_id: str,
    build_id: List[str],
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListBatchesOutput]]:
    """  Returns the batches for a build.

    Args:
        project_id (str):
        branch_id (str):
        build_id (List[str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListBatchesOutput]
     """


    return sync_detailed(
        project_id=project_id,
branch_id=branch_id,
build_id=build_id,
client=client,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    branch_id: str,
    build_id: List[str],
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListBatchesOutput]]:
    """  Returns the batches for a build.

    Args:
        project_id (str):
        branch_id (str):
        build_id (List[str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListBatchesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
branch_id=branch_id,
build_id=build_id,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    branch_id: str,
    build_id: List[str],
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListBatchesOutput]]:
    """  Returns the batches for a build.

    Args:
        project_id (str):
        branch_id (str):
        build_id (List[str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListBatchesOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
branch_id=branch_id,
build_id=build_id,
client=client,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
