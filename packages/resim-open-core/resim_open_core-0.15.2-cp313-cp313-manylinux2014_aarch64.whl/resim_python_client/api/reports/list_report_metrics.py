from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_report_metrics_output import ListReportMetricsOutput
from typing import cast
from ...types import UNSET, Unset
from typing import Union
from typing import Dict



def _get_kwargs(
    project_id: str,
    report_id: str,
    *,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Dict[str, Any]:
    

    

    params: Dict[str, Any] = {}

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/reports/{report_id}/metrics".format(project_id=project_id,report_id=report_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, ListReportMetricsOutput]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListReportMetricsOutput.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, ListReportMetricsOutput]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListReportMetricsOutput]]:
    """  Lists the metrics for a given report. Does not return associated data.

    Args:
        project_id (str):
        report_id (str):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListReportMetricsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
report_id=report_id,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListReportMetricsOutput]]:
    """  Lists the metrics for a given report. Does not return associated data.

    Args:
        project_id (str):
        report_id (str):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListReportMetricsOutput]
     """


    return sync_detailed(
        project_id=project_id,
report_id=report_id,
client=client,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Response[Union[Any, ListReportMetricsOutput]]:
    """  Lists the metrics for a given report. Does not return associated data.

    Args:
        project_id (str):
        report_id (str):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ListReportMetricsOutput]]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
report_id=report_id,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    report_id: str,
    *,
    client: AuthenticatedClient,
    page_size: Union[Unset, int] = UNSET,
    page_token: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, ListReportMetricsOutput]]:
    """  Lists the metrics for a given report. Does not return associated data.

    Args:
        project_id (str):
        report_id (str):
        page_size (Union[Unset, int]):
        page_token (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ListReportMetricsOutput]
     """


    return (await asyncio_detailed(
        project_id=project_id,
report_id=report_id,
client=client,
page_size=page_size,
page_token=page_token,

    )).parsed
