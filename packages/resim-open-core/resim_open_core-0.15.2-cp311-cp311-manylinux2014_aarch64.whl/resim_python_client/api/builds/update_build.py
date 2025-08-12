from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import Dict
from typing import cast
from ...models.update_build_input import UpdateBuildInput
from ...models.build import Build



def _get_kwargs(
    project_id: str,
    build_id: str,
    *,
    body: UpdateBuildInput,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/builds/{build_id}".format(project_id=project_id,build_id=build_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Build]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Build.from_dict(response.json())



        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Build]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Response[Union[Any, Build]]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Build]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
build_id=build_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Optional[Union[Any, Build]]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Build]
     """


    return sync_detailed(
        project_id=project_id,
build_id=build_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Response[Union[Any, Build]]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Build]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
build_id=build_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Optional[Union[Any, Build]]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Build]
     """


    return (await asyncio_detailed(
        project_id=project_id,
build_id=build_id,
client=client,
body=body,

    )).parsed
