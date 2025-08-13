from diracx.core.models import SearchSpec, SortSpec
from pydantic import BaseModel


class BKSummaryParams(BaseModel):
    grouping: list[str]
    search: list[SearchSpec] = []
    # TODO: Add more validation


class BKSearchParams(BaseModel):
    parameters: list[str] | None = None
    search: list[SearchSpec] = []
    sort: list[SortSpec] = []
    distinct: bool = False
    # TODO: Add more validation
