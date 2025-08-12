from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import cast
from ...types import UNSET, Unset
from typing import Union
from typing import Dict
from ...models.list_job_event_tags_output import ListJobEventTagsOutput



def _get_kwargs(
    project_id: str,
    batch_id: str,
    job_id: str,
    *,
    name: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["name"] = name

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/batches/{batch_id}/jobs/{job_id}/eventTags".format(project_id=project_id,batch_id=batch_id,job_id=job_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListJobEventTagsOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListJobEventTagsOutput.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListJobEventTagsOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    job_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListJobEventTagsOutput]]:
    """  Lists the event tags for a given job.

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        name (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListJobEventTagsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
name=name,
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
    job_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListJobEventTagsOutput]]:
    """  Lists the event tags for a given job.

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        name (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListJobEventTagsOutput]
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
client=client,
name=name,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    job_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListJobEventTagsOutput]]:
    """  Lists the event tags for a given job.

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        name (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListJobEventTagsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
name=name,
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
    job_id: str,
    *,
    client: AuthenticatedClient,
    name: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListJobEventTagsOutput]]:
    """  Lists the event tags for a given job.

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        name (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListJobEventTagsOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
client=client,
name=name,
page_size=page_size,
page_token=page_token,

    )).parsed
