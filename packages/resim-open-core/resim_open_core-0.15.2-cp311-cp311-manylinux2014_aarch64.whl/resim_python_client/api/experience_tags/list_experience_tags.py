from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import Dict
from ...models.list_experience_tags_order_by import ListExperienceTagsOrderBy
from typing import cast
from ...types import UNSET, Unset
from ...models.list_experience_tags_output import ListExperienceTagsOutput
from typing import Union



def _get_kwargs(
    project_id: str,
    *,
    name: Union[Unset, str] = UNSET,
    order_by: Union[Unset, ListExperienceTagsOrderBy] = ListExperienceTagsOrderBy.ID,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["name"] = name

    json_order_by: Union[Unset, str] = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/experienceTags".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListExperienceTagsOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListExperienceTagsOutput.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListExperienceTagsOutput]]:
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
    order_by: Union[Unset, ListExperienceTagsOrderBy] = ListExperienceTagsOrderBy.ID,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperienceTagsOutput]]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        order_by (Union[Unset, ListExperienceTagsOrderBy]):  Default:
            ListExperienceTagsOrderBy.ID.
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperienceTagsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

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
    order_by: Union[Unset, ListExperienceTagsOrderBy] = ListExperienceTagsOrderBy.ID,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperienceTagsOutput]]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        order_by (Union[Unset, ListExperienceTagsOrderBy]):  Default:
            ListExperienceTagsOrderBy.ID.
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperienceTagsOutput]
     """


    return sync_detailed(
        project_id=project_id,
client=client,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    order_by: Union[Unset, ListExperienceTagsOrderBy] = ListExperienceTagsOrderBy.ID,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperienceTagsOutput]]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        order_by (Union[Unset, ListExperienceTagsOrderBy]):  Default:
            ListExperienceTagsOrderBy.ID.
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperienceTagsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

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
    order_by: Union[Unset, ListExperienceTagsOrderBy] = ListExperienceTagsOrderBy.ID,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperienceTagsOutput]]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (Union[Unset, str]):
        order_by (Union[Unset, ListExperienceTagsOrderBy]):  Default:
            ListExperienceTagsOrderBy.ID.
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperienceTagsOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

    )).parsed
