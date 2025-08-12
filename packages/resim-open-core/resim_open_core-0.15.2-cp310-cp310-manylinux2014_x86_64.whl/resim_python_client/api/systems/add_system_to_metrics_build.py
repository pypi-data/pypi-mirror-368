from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    project_id: str,
    system_id: str,
    metrics_build_id: str,

) -> Dict[str, Any]:
    

    

    

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_id}/systems/{system_id}/metricsBuilds/{metrics_build_id}".format(project_id=project_id,system_id=system_id,metrics_build_id=metrics_build_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.CREATED:
        return None
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    if response.status_code == HTTPStatus.CONFLICT:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    system_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any]:
    """  Registers the given metrics build as applicable for the system

    Args:
        project_id (str):
        system_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
system_id=system_id,
metrics_build_id=metrics_build_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    project_id: str,
    system_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any]:
    """  Registers the given metrics build as applicable for the system

    Args:
        project_id (str):
        system_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
system_id=system_id,
metrics_build_id=metrics_build_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

