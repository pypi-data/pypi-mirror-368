from pydantic import BaseModel, Field
from maleo_soma.mixins.general import Key, Name
from maleo_soma.types.base import OptionalString


class UrlSlug(BaseModel):
    url_slug: OptionalString = Field(None, description="URL Slug")


class ResourceIdentifier(Name, Key, UrlSlug):
    pass
