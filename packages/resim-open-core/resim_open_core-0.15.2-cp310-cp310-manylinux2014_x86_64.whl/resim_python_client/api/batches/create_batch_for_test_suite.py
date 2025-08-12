from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from typing import cast
from ...models.test_suite_batch_input import TestSuiteBatchInput
from ...models.batch import Batch
from typing import Dict



def _get_kwargs(
    project_id: str,
    test_suite_id: str,
    *,
    body: TestSuiteBatchInput,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_id}/suites/{test_suite_id}/batches".format(project_id=project_id,test_suite_id=test_suite_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Batch]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = Batch.from_dict(response.json())



        return response_201
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.PAYMENT_REQUIRED:
        response_402 = cast(Any, None)
        return response_402
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
    test_suite_id: str,
    *,
    client: AuthenticatedClient,
    body: TestSuiteBatchInput,

) -> Response[Union[Any, Batch]]:
    """  Creates a batch for that test suite

    Args:
        project_id (str):
        test_suite_id (str):
        body (TestSuiteBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Batch]]
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
    body: TestSuiteBatchInput,

) -> Optional[Union[Any, Batch]]:
    """  Creates a batch for that test suite

    Args:
        project_id (str):
        test_suite_id (str):
        body (TestSuiteBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Batch]
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
    body: TestSuiteBatchInput,

) -> Response[Union[Any, Batch]]:
    """  Creates a batch for that test suite

    Args:
        project_id (str):
        test_suite_id (str):
        body (TestSuiteBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Batch]]
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
    body: TestSuiteBatchInput,

) -> Optional[Union[Any, Batch]]:
    """  Creates a batch for that test suite

    Args:
        project_id (str):
        test_suite_id (str):
        body (TestSuiteBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Batch]
     """


    return (await asyncio_detailed(
        project_id=project_id,
test_suite_id=test_suite_id,
client=client,
body=body,

    )).parsed
