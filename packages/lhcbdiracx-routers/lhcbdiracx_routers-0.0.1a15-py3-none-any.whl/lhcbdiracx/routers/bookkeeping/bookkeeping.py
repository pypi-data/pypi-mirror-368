from __future__ import annotations

from http import HTTPStatus
from typing import Annotated, Any

from diracx.routers.fastapi_classes import DiracxRouter
from fastapi import Body, Depends, Response
from fastapi.responses import StreamingResponse

from lhcbdiracx.core.models import BKSearchParams, BKSummaryParams
from lhcbdiracx.db.sql import BookkeepingDB as _BookkeepingDB
from lhcbdiracx.logic.bookkeeping.bookkeeping import dump_bk_paths
from lhcbdiracx.logic.bookkeeping.bookkeeping import hello_world as hello_world_bl
from lhcbdiracx.logic.bookkeeping.bookkeeping import (
    search_datasets as search_datasets_bl,
)
from lhcbdiracx.logic.bookkeeping.bookkeeping import (
    search_files as search_files_bl,
)
from lhcbdiracx.logic.bookkeeping.bookkeeping import (
    summary_datasets as summary_datasets_bl,
)
from lhcbdiracx.logic.bookkeeping.bookkeeping import (
    summary_files as summary_files_bl,
)

from .access_policy import ActionType, CheckBookkeepingPolicyCallable

router = DiracxRouter()

# Define the dependency at the top, so you don't have to
# be so verbose in your routes
BookkeepingDB = Annotated[_BookkeepingDB, Depends(_BookkeepingDB.transaction)]


@router.get("/")
async def hello_world(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
):
    await check_permission(action=ActionType.HELLO)
    return await hello_world_bl(bookkeeping_db)


@router.get(
    "/dump-paths",
    response_class=StreamingResponse,
    response_description="A text dump of all possible bookkeeping paths with one path per line.",
)
async def dump_paths(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
):
    await check_permission(action=ActionType.READ)
    return StreamingResponse(dump_bk_paths(bookkeeping_db), media_type="text/plain")


EXAMPLE_SEARCHES = {
    "Get bookkeeping paths": {
        "summary": "Get all paths for 2016 data and MC",
        "description": "Get Bookkeeping Paths for 2016 data and MC, ordered alphabetically (asc) by BkPath",
        "value": {
            "parameters": ["BkPath"],
            "search": [
                {"parameter": "ConfigName", "operator": "in", "values": ["LHCb", "MC"]},
                {
                    "parameter": "ConfigVersion",
                    "operator": "in",
                    "values": ["Collision16", "2016"],
                },
            ],
            "sort": [{"parameter": "BkPath", "direction": "asc"}],
        },
    },
}


@router.post("/datasets/search")
async def search_datasets(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
    response: Response,
    page: int = 1,
    per_page: int = 100,
    body: Annotated[
        BKSearchParams | None, Body(openapi_examples=EXAMPLE_SEARCHES)
    ] = None,
) -> list[dict[str, Any]]:
    """Retrieve information about bookkeeping datasets.

    **TODO: Add more docs**
    """
    await check_permission(action=ActionType.READ)

    total, jobs = await search_datasets_bl(
        bookkeeping_db=bookkeeping_db,
        page=page,
        per_page=per_page,
        body=body,
    )

    # Set the Content-Range header if needed
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4

    # No jobs found but there are jobs for the requested search
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4.4
    if len(jobs) == 0 and total > 0:
        response.headers["Content-Range"] = f"jobs */{total}"
        response.status_code = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE

    # The total number of jobs is greater than the number of jobs returned
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4.2
    elif len(jobs) < total:
        first_idx = per_page * (page - 1)
        last_idx = min(first_idx + len(jobs), total) - 1 if total > 0 else 0
        response.headers["Content-Range"] = f"jobs {first_idx}-{last_idx}/{total}"
        response.status_code = HTTPStatus.PARTIAL_CONTENT
    return jobs


@router.post("/datasets/summary")
async def summary_datasets(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
    body: BKSummaryParams,
):
    """Show information suitable for plotting."""
    await check_permission(action=ActionType.READ, bookkeeping_db=bookkeeping_db)

    return await summary_datasets_bl(
        bookkeeping_db=bookkeeping_db,
        body=body,
    )


@router.post("/datasets/files/search")
async def search_files(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
    response: Response,
    page: int = 1,
    per_page: int = 100,
    body: Annotated[
        BKSearchParams | None, Body(openapi_examples=EXAMPLE_SEARCHES)
    ] = None,
) -> list[dict[str, Any]]:
    """Retrieve information about files under bookkeeping datasets.

    **TODO: Add more docs**
    """
    await check_permission(action=ActionType.READ)

    total, jobs = await search_files_bl(
        bookkeeping_db=bookkeeping_db,
        page=page,
        per_page=per_page,
        body=body,
    )

    # Set the Content-Range header if needed
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4

    # No jobs found but there are jobs for the requested search
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4.4
    if len(jobs) == 0 and total > 0:
        response.headers["Content-Range"] = f"jobs */{total}"
        response.status_code = HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE

    # The total number of jobs is greater than the number of jobs returned
    # https://datatracker.ietf.org/doc/html/rfc7233#section-4.2
    elif len(jobs) < total:
        first_idx = per_page * (page - 1)
        last_idx = min(first_idx + len(jobs), total) - 1 if total > 0 else 0
        response.headers["Content-Range"] = f"jobs {first_idx}-{last_idx}/{total}"
        response.status_code = HTTPStatus.PARTIAL_CONTENT
    return jobs


@router.post("/datasets/files/summary")
async def summary_files(
    bookkeeping_db: BookkeepingDB,
    check_permission: CheckBookkeepingPolicyCallable,
    body: BKSummaryParams,
):
    """Show information suitable for plotting."""
    await check_permission(action=ActionType.READ, bookkeeping_db=bookkeeping_db)

    return await summary_files_bl(
        bookkeeping_db=bookkeeping_db,
        body=body,
    )
