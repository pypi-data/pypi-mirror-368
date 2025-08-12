from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.report import Report
from ...models.report_input import ReportInput
from typing import cast
from typing import Dict



def _get_kwargs(
    project_id: str,
    *,
    body: ReportInput,

) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}


    

    

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/projects/{project_id}/reports".format(project_id=project_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Report]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = Report.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Report]]:
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
    body: ReportInput,

) -> Response[Union[Any, Report]]:
    """  Adds a report. If the user supplies a name parameter, that name will be used, otherwise a name will
    be generated. The end timestamp is optional and will default to now(). The respectRevisionBoundary
    field enables strict report generation from only the defined testSuiteRevision.

    Args:
        project_id (str):
        body (ReportInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Report]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: ReportInput,

) -> Optional[Union[Any, Report]]:
    """  Adds a report. If the user supplies a name parameter, that name will be used, otherwise a name will
    be generated. The end timestamp is optional and will default to now(). The respectRevisionBoundary
    field enables strict report generation from only the defined testSuiteRevision.

    Args:
        project_id (str):
        body (ReportInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Report]
     """


    return sync_detailed(
        project_id=project_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: ReportInput,

) -> Response[Union[Any, Report]]:
    """  Adds a report. If the user supplies a name parameter, that name will be used, otherwise a name will
    be generated. The end timestamp is optional and will default to now(). The respectRevisionBoundary
    field enables strict report generation from only the defined testSuiteRevision.

    Args:
        project_id (str):
        body (ReportInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Report]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
    body: ReportInput,

) -> Optional[Union[Any, Report]]:
    """  Adds a report. If the user supplies a name parameter, that name will be used, otherwise a name will
    be generated. The end timestamp is optional and will default to now(). The respectRevisionBoundary
    field enables strict report generation from only the defined testSuiteRevision.

    Args:
        project_id (str):
        body (ReportInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Report]
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
body=body,

    )).parsed
