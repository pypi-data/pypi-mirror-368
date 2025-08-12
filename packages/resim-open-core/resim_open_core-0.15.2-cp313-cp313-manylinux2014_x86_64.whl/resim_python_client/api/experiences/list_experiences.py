from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import cast
from ...types import UNSET, Unset
from typing import Union
from ...models.list_experiences_output import ListExperiencesOutput
from typing import Dict



def _get_kwargs(
    project_id: str,
    *,
    name: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["name"] = name

    params["text"] = text

    params["search"] = search

    params["archived"] = archived

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/experiences".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListExperiencesOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListExperiencesOutput.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListExperiencesOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperiencesOutput]]:
    """  Returns the list of experiences.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        text (Union[Unset, str]):
        search (Union[Unset, str]):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperiencesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
text=text,
search=search,
archived=archived,
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
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperiencesOutput]]:
    """  Returns the list of experiences.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        text (Union[Unset, str]):
        search (Union[Unset, str]):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperiencesOutput]
     """


    return sync_detailed(
        project_id=project_id,
client=client,
name=name,
text=text,
search=search,
archived=archived,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperiencesOutput]]:
    """  Returns the list of experiences.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        text (Union[Unset, str]):
        search (Union[Unset, str]):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperiencesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
text=text,
search=search,
archived=archived,
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
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    text: Union[Unset, str] = UNSET,
    search: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperiencesOutput]]:
    """  Returns the list of experiences.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        text (Union[Unset, str]):
        search (Union[Unset, str]):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperiencesOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
name=name,
text=text,
search=search,
archived=archived,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
