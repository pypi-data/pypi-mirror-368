from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_test_suite_output import ListTestSuiteOutput
from typing import Union
from typing import cast, List
from typing import cast
from ...types import UNSET, Unset
from typing import Dict



def _get_kwargs(
    project_id: str,
    *,
    experience_i_ds: Union[Unset, List[str]] = UNSET,
    system_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    text: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    json_experience_i_ds: Union[Unset, List[str]] = UNSET
    if not isinstance(experience_i_ds, Unset):
        json_experience_i_ds = experience_i_ds


    params["experienceIDs"] = json_experience_i_ds

    params["systemID"] = system_id

    params["name"] = name

    params["archived"] = archived

    params["text"] = text

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/suites".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListTestSuiteOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListTestSuiteOutput.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListTestSuiteOutput]]:
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
    experience_i_ds: Union[Unset, List[str]] = UNSET,
    system_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    text: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListTestSuiteOutput]]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (Union[Unset, List[str]]):
        system_id (Union[Unset, str]):
        name (Union[Unset, str]):
        archived (Union[Unset, bool]):
        text (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListTestSuiteOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_i_ds=experience_i_ds,
system_id=system_id,
name=name,
archived=archived,
text=text,
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
    experience_i_ds: Union[Unset, List[str]] = UNSET,
    system_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    text: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListTestSuiteOutput]]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (Union[Unset, List[str]]):
        system_id (Union[Unset, str]):
        name (Union[Unset, str]):
        archived (Union[Unset, bool]):
        text (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListTestSuiteOutput]
     """


    return sync_detailed(
        project_id=project_id,
client=client,
experience_i_ds=experience_i_ds,
system_id=system_id,
name=name,
archived=archived,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    experience_i_ds: Union[Unset, List[str]] = UNSET,
    system_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    text: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListTestSuiteOutput]]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (Union[Unset, List[str]]):
        system_id (Union[Unset, str]):
        name (Union[Unset, str]):
        archived (Union[Unset, bool]):
        text (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListTestSuiteOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_i_ds=experience_i_ds,
system_id=system_id,
name=name,
archived=archived,
text=text,
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
    experience_i_ds: Union[Unset, List[str]] = UNSET,
    system_id: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    archived: Union[Unset, bool] = UNSET,
    text: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,
    order_by: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListTestSuiteOutput]]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (Union[Unset, List[str]]):
        system_id (Union[Unset, str]):
        name (Union[Unset, str]):
        archived (Union[Unset, bool]):
        text (Union[Unset, str]):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):
        order_by (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListTestSuiteOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
experience_i_ds=experience_i_ds,
system_id=system_id,
name=name,
archived=archived,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
