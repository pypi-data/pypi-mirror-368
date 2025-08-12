from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.revise_test_suite_input import ReviseTestSuiteInput
from typing import cast
from typing import Dict
from ...models.test_suite import TestSuite



def _get_kwargs(
    project_id: str,
    test_suite_id: str,
    *,
    body: ReviseTestSuiteInput,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/suites/{test_suite_id}".format(project_id=project_id,test_suite_id=test_suite_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, TestSuite]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = TestSuite.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, TestSuite]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,
    body: ReviseTestSuiteInput,

) -> Response[Union[Any, TestSuite]]:
    """  Revise a test suite, generating a new revision. Supply a false value for ad-hoc to convert an
    existing ad hoc test suite to a full test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        body (ReviseTestSuiteInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TestSuite]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
test_suite_id=test_suite_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,
    body: ReviseTestSuiteInput,

) -> Optional[Union[Any, TestSuite]]:
    """  Revise a test suite, generating a new revision. Supply a false value for ad-hoc to convert an
    existing ad hoc test suite to a full test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        body (ReviseTestSuiteInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TestSuite]
     """


    return sync_detailed(
        project_id=project_id,
test_suite_id=test_suite_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,
    body: ReviseTestSuiteInput,

) -> Response[Union[Any, TestSuite]]:
    """  Revise a test suite, generating a new revision. Supply a false value for ad-hoc to convert an
    existing ad hoc test suite to a full test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        body (ReviseTestSuiteInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, TestSuite]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
test_suite_id=test_suite_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,
    body: ReviseTestSuiteInput,

) -> Optional[Union[Any, TestSuite]]:
    """  Revise a test suite, generating a new revision. Supply a false value for ad-hoc to convert an
    existing ad hoc test suite to a full test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        body (ReviseTestSuiteInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, TestSuite]
     """


    return (await asyncio_detailed(
        project_id=project_id,
test_suite_id=test_suite_id,
client=client,
body=body,

    )).parsed
