from pydantic import BaseModel, Field, model_validator
from typing import Any, Generic, Optional, Self, TypeVar, Union
from maleo_soma.enums.pagination import Limit


class Page(BaseModel):
    page: int = Field(1, ge=1, description="Page number, must be >= 1.")


class FlexibleLimit(BaseModel):
    limit: Optional[Limit] = Field(None, description="Page limit. (Optional)")


class StrictLimit(BaseModel):
    limit: Limit = Field(Limit.LIM_10, description="Page limit.")


class PageInfo(BaseModel):
    data_count: int = Field(..., description="Fetched data count")
    total_data: int = Field(..., description="Total data count")
    total_pages: int = Field(..., description="Total pages count")


class BaseFlexiblePagination(FlexibleLimit, Page):
    @model_validator(mode="after")
    def validate_page_and_limit(self) -> Self:
        if self.limit is None:
            self.page = 1
        return self


class FlexiblePagination(PageInfo, BaseFlexiblePagination):
    pass


class BaseStrictPagination(StrictLimit, Page):
    pass


class StrictPagination(PageInfo, BaseStrictPagination):
    pass


# ! Do not instantiate and use this class
# * This class is created for future type override
class AnyPaginationMixin(BaseModel):
    pagination: Any = Field(..., description="Pagination")


class NoPaginationMixin(AnyPaginationMixin):
    pagination: None = None


PaginationT = TypeVar("PaginationT", bound=Union[FlexiblePagination, StrictPagination])


class PaginationMixin(AnyPaginationMixin, Generic[PaginationT]):
    pagination: PaginationT = Field(..., description="Pagination")


class OptionalPaginationMixin(AnyPaginationMixin, Generic[PaginationT]):
    pagination: Optional[PaginationT] = Field(
        None, description="Pagination. (Optional)"
    )
