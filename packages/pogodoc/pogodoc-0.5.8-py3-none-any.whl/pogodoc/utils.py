import httpx
import pydantic
import typing
from pogodoc.client.documents.types import (
    InitializeRenderJobRequestType,
    InitializeRenderJobRequestFormatOpts,
    InitializeRenderJobRequestTarget,
)
from pogodoc.client.core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel

def upload_to_s3_with_url(presigned_url: str, payload, payload_length, content_type: str):
    headers = {
        "Content-Length": str(payload_length),
    }

    if content_type:
        headers["Content-Type"] = content_type

    httpx.put(presigned_url, content=payload, headers=headers)

class RenderConfig(UniversalBaseModel):
    type: InitializeRenderJobRequestType
    target: InitializeRenderJobRequestTarget
    format_opts: typing.Optional[InitializeRenderJobRequestFormatOpts] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
