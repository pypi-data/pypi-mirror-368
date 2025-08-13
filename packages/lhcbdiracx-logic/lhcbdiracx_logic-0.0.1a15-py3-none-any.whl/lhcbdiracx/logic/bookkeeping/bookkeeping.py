from __future__ import annotations

import logging
from typing import Any

from lhcbdiracx.core.models import BKSearchParams, BKSummaryParams
from lhcbdiracx.db.sql import BookkeepingDB

logger = logging.getLogger(__name__)


MAX_PER_PAGE = 10000


async def hello_world(
    bookkeeping_db: BookkeepingDB,
):
    return await bookkeeping_db.hello()


async def dump_bk_paths(bookkeeping_db: BookkeepingDB):
    async with bookkeeping_db as bookkeeping_db:
        async for bk_path in bookkeeping_db.dump_all_bk_paths():
            yield f"{bk_path}\n"


async def search_datasets(
    bookkeeping_db: BookkeepingDB,
    page: int = 1,
    per_page: int = 100,
    body: BKSearchParams | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    """Retrieve information about bookkeeping datasets."""
    # Apply a limit to per_page to prevent abuse of the API
    if per_page > MAX_PER_PAGE:
        per_page = MAX_PER_PAGE

    if body is None:
        body = BKSearchParams()

    total, datasets = await bookkeeping_db.search(
        body.parameters,
        body.search,
        body.sort,
        distinct=body.distinct,
        page=page,
        per_page=per_page,
    )

    return total, datasets


async def summary_datasets(
    bookkeeping_db: BookkeepingDB,
    body: BKSummaryParams,
):
    """Show information suitable for plotting."""
    return await bookkeeping_db.summary(body.grouping, body.search)


async def search_files(
    bookkeeping_db: BookkeepingDB,
    page: int = 1,
    per_page: int = 100,
    body: BKSearchParams | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    """Retrieve information about bookkeeping files."""
    # Apply a limit to per_page to prevent abuse of the API
    if per_page > MAX_PER_PAGE:
        per_page = MAX_PER_PAGE

    if body is None:
        body = BKSearchParams()

    total, files = await bookkeeping_db.search_files(
        body.parameters,
        body.search,
        body.sort,
        distinct=body.distinct,
        page=page,
        per_page=per_page,
    )

    return total, files


async def summary_files(
    bookkeeping_db: BookkeepingDB,
    body: BKSummaryParams,
):
    """Show information suitable for plotting."""
    return await bookkeeping_db.summary_files(body.grouping, body.search)
