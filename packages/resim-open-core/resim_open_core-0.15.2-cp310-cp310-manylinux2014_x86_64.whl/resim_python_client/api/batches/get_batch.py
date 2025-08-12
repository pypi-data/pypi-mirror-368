from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import cast
from ...models.batch import Batch
from typing import Dict



def _get_kwargs(
    project_id: str,
    batch_id: str,

) -> Dict[str, Any]:
    

    

    

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/batches/{batch_id}".format(project_id=project_id,batch_id=batch_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Batch]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Batch.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Batch]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, Batch]]:
    """  Returns a batch.

    Args:
        project_id (str):
        batch_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Batch]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, Batch]]:
    """  Returns a batch.

    Args:
        project_id (str):
        batch_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Batch]
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, Batch]]:
    """  Returns a batch.

    Args:
        project_id (str):
        batch_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Batch]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, Batch]]:
    """  Returns a batch.

    Args:
        project_id (str):
        batch_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Batch]
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,

    )).parsed
