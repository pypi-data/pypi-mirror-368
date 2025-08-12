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
    experience_tag_id: str,
    *,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["archived"] = archived

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/experienceTags/{experience_tag_id}/experiences".format(project_id=project_id,experience_tag_id=experience_tag_id,),
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
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperiencesOutput]]:
    """  Returns a list of experiences with the given experience tag.

    Args:
        project_id (str):
        experience_tag_id (str):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperiencesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_tag_id=experience_tag_id,
archived=archived,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperiencesOutput]]:
    """  Returns a list of experiences with the given experience tag.

    Args:
        project_id (str):
        experience_tag_id (str):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperiencesOutput]
     """


    return sync_detailed(
        project_id=project_id,
experience_tag_id=experience_tag_id,
client=client,
archived=archived,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListExperiencesOutput]]:
    """  Returns a list of experiences with the given experience tag.

    Args:
        project_id (str):
        experience_tag_id (str):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListExperiencesOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_tag_id=experience_tag_id,
archived=archived,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    archived: Union[Unset, bool] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListExperiencesOutput]]:
    """  Returns a list of experiences with the given experience tag.

    Args:
        project_id (str):
        experience_tag_id (str):
        archived (Union[Unset, bool]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListExperiencesOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
experience_tag_id=experience_tag_id,
client=client,
archived=archived,
page_size=page_size,
page_token=page_token,

    )).parsed
