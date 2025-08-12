from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.batch_log import BatchLog
from typing import cast
from typing import Dict



def _get_kwargs(
    project_id: str,
    batch_id: str,
    log_id: str,

) -> Dict[str, Any]:
    

    

    

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/batches/{batch_id}/logs/{log_id}".format(project_id=project_id,batch_id=batch_id,log_id=log_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, BatchLog]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = BatchLog.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, BatchLog]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    log_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, BatchLog]]:
    """  Get an individual log file

    Args:
        project_id (str):
        batch_id (str):
        log_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BatchLog]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
log_id=log_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    batch_id: str,
    log_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, BatchLog]]:
    """  Get an individual log file

    Args:
        project_id (str):
        batch_id (str):
        log_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BatchLog]
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
log_id=log_id,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    log_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, BatchLog]]:
    """  Get an individual log file

    Args:
        project_id (str):
        batch_id (str):
        log_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, BatchLog]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
log_id=log_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    batch_id: str,
    log_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, BatchLog]]:
    """  Get an individual log file

    Args:
        project_id (str):
        batch_id (str):
        log_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, BatchLog]
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
log_id=log_id,
client=client,

    )).parsed
