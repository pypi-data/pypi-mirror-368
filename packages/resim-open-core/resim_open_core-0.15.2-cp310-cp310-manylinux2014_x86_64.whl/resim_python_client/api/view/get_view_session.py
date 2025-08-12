from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.view_object_and_metadata import ViewObjectAndMetadata
from typing import cast
from typing import Dict



def _get_kwargs(
    view_session_id: str,

) -> Dict[str, Any]:
    

    

    

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/view/sessions/{view_session_id}".format(view_session_id=view_session_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ViewObjectAndMetadata]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ViewObjectAndMetadata.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ViewObjectAndMetadata]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    view_session_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, ViewObjectAndMetadata]]:
    """  Lists the view object and metadata associated with a specific view.

    Args:
        view_session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ViewObjectAndMetadata]]
     """


    kwargs = _get_kwargs(
        view_session_id=view_session_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    view_session_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, ViewObjectAndMetadata]]:
    """  Lists the view object and metadata associated with a specific view.

    Args:
        view_session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ViewObjectAndMetadata]
     """


    return sync_detailed(
        view_session_id=view_session_id,
client=client,

    ).parsed

async def asyncio_detailed(
    view_session_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, ViewObjectAndMetadata]]:
    """  Lists the view object and metadata associated with a specific view.

    Args:
        view_session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ViewObjectAndMetadata]]
     """


    kwargs = _get_kwargs(
        view_session_id=view_session_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    view_session_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, ViewObjectAndMetadata]]:
    """  Lists the view object and metadata associated with a specific view.

    Args:
        view_session_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ViewObjectAndMetadata]
     """


    return (await asyncio_detailed(
        view_session_id=view_session_id,
client=client,

    )).parsed
