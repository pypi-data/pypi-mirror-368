import re
import urllib.parse
from pydantic import BaseModel, Field, field_validator
from enum import StrEnum
from typing import Generic, List, TypeVar
from uuid import UUID
from maleo_soma.constants import DATE_FILTER_PATTERN, SORT_COLUMN_PATTERN
from maleo_soma.enums.sort import SortOrder
from maleo_soma.enums.status import DataStatus
from maleo_soma.schemas.filter import DateFilter
from maleo_soma.schemas.sort import SortColumn
from maleo_soma.types.base import (
    ListOfStrings,
    OptionalListOfDataStatuses as OptionalListOfDataStatusesEnum,
    OptionalListOfIntegers,
    OptionalListOfStrings,
    OptionalListOfUUIDs,
    OptionalString,
)


IdentifierTypeT = TypeVar("IdentifierTypeT", bound=StrEnum)


class IdentifierType(BaseModel, Generic[IdentifierTypeT]):
    identifier: IdentifierTypeT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class OptionalListOfIds(BaseModel):
    ids: OptionalListOfIntegers = Field(None, description="Specific Ids")

    @field_validator("ids", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, int):
            values = [values]

        return values


class OptionalListOfOrganizationIds(BaseModel):
    organization_ids: OptionalListOfIntegers = Field(
        None, description="Specific Organization Ids"
    )

    @field_validator("organization_ids", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, int):
            values = [values]

        return values


class OptionalListOfParentIds(BaseModel):
    parent_ids: OptionalListOfIntegers = Field(None, description="Specific Parent Ids")

    @field_validator("parent_ids", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, int):
            values = [values]

        return values


class OptionalListOfUserIds(BaseModel):
    user_ids: OptionalListOfIntegers = Field(None, description="Specific User Ids")

    @field_validator("user_ids", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, int):
            values = [values]

        return values


class OptionalListOfUuids(BaseModel):
    uuids: OptionalListOfUUIDs = Field(None, description="Specific Uuids")

    @field_validator("uuids", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single UUID case
        if isinstance(values, UUID):
            values = [values]

        return values


class Filters(BaseModel):
    filters: ListOfStrings = Field(
        [],
        description="Filters for date range, e.g. 'created_at|from::<ISO_DATETIME>|to::<ISO_DATETIME>'.",
    )

    @field_validator("filters", mode="before")
    @classmethod
    def validate_date_filters(cls, values):
        if isinstance(values, list):
            decoded_values = [urllib.parse.unquote(value) for value in values]
            # * Replace space followed by 2 digits, colon, 2 digits with + and those digits
            fixed_values = []
            for value in decoded_values:
                # * Look for the pattern: space followed by 2 digits, colon, 2 digits
                fixed_value = re.sub(
                    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) (\d{2}:\d{2})",
                    r"\1+\2",
                    value,
                )
                fixed_values.append(fixed_value)
            final_values = [
                value for value in fixed_values if DATE_FILTER_PATTERN.match(value)
            ]
            return final_values


class DateFilters(BaseModel):
    date_filters: List[DateFilter] = Field([], description="Date filters to be applied")


class OptionalListOfDataStatuses(BaseModel):
    statuses: OptionalListOfDataStatusesEnum = Field(None, description="Data's status")

    @field_validator("statuses", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, DataStatus):
            values = [values]

        return values


class OptionalListOfCodes(BaseModel):
    codes: OptionalListOfStrings = Field(None, description="Specific Codes")

    @field_validator("codes", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, str):
            values = [values]

        return values


class OptionalListOfKeys(BaseModel):
    keys: OptionalListOfStrings = Field(None, description="Specific Keys")

    @field_validator("keys", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, str):
            values = [values]

        return values


class OptionalListOfNames(BaseModel):
    names: OptionalListOfStrings = Field(None, description="Specific Names")

    @field_validator("names", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, str):
            values = [values]

        return values


class Search(BaseModel):
    search: OptionalString = Field(None, description="Search string.")


class Sorts(BaseModel):
    sorts: ListOfStrings = Field(
        ["id.asc"],
        description="Sorting columns in 'column_name.asc' or 'column_name.desc' format.",
    )

    @field_validator("sorts", mode="before")
    @classmethod
    def validate_sorts(cls, values):
        # Handle single string case
        if isinstance(values, str):
            values = [values]

        # Now validate the list
        if isinstance(values, list):
            return [value for value in values if SORT_COLUMN_PATTERN.match(value)]

        return values


class SortColumns(BaseModel):
    sort_columns: List[SortColumn] = Field(
        [SortColumn(name="id", order=SortOrder.ASC)],
        description="List of columns to be sorted",
    )


class Expand(BaseModel):
    expand: OptionalListOfStrings = Field(None, description="Expanded field(s)")

    @field_validator("expand", mode="before")
    @classmethod
    def validate_ids(cls, values):
        # Handle single int case
        if isinstance(values, str):
            values = [values]

        return values
