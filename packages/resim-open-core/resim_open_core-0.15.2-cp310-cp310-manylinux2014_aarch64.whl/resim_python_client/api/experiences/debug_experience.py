from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.debug_experience_output import DebugExperienceOutput
from typing import cast
from ...models.debug_experience_input import DebugExperienceInput
from typing import Dict



def _get_kwargs(
    project_id: str,
    experience_id: str,
    *,
    body: DebugExperienceInput,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_id}/experiences/{experience_id}/debug".format(project_id=project_id,experience_id=experience_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, DebugExperienceOutput]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = DebugExperienceOutput.from_dict(response.json())



        return response_201
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, DebugExperienceOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: DebugExperienceInput,

) -> Response[Union[Any, DebugExperienceOutput]]:
    """  Reruns an experience in debug mode.

    Args:
        project_id (str):
        experience_id (str):
        body (DebugExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DebugExperienceOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_id=experience_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: DebugExperienceInput,

) -> Optional[Union[Any, DebugExperienceOutput]]:
    """  Reruns an experience in debug mode.

    Args:
        project_id (str):
        experience_id (str):
        body (DebugExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DebugExperienceOutput]
     """


    return sync_detailed(
        project_id=project_id,
experience_id=experience_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: DebugExperienceInput,

) -> Response[Union[Any, DebugExperienceOutput]]:
    """  Reruns an experience in debug mode.

    Args:
        project_id (str):
        experience_id (str):
        body (DebugExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DebugExperienceOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_id=experience_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: DebugExperienceInput,

) -> Optional[Union[Any, DebugExperienceOutput]]:
    """  Reruns an experience in debug mode.

    Args:
        project_id (str):
        experience_id (str):
        body (DebugExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DebugExperienceOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
experience_id=experience_id,
client=client,
body=body,

    )).parsed
