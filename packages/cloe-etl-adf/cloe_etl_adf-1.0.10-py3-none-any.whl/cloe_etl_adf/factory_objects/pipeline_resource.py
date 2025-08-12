import datetime
import logging
from typing import Literal

from cloe_metadata.utils import writer
from pydantic import BaseModel, ConfigDict, Field

from .execute_pipeline_activity import ExecutePipelineActivity

logger = logging.getLogger(__name__)


class PipelineResourceProperties(BaseModel):
    activities: list[ExecutePipelineActivity]
    parameters: dict[str, str] = {}
    variables: dict[str, str] = {}
    folder: dict[str, str] = {}
    annotations: list[str] = []
    last_publish_time: str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )


class PipelineResource(BaseModel):
    name: str
    properties: PipelineResourceProperties
    arm_type: Literal["Microsoft.DataFactory/factories/pipelines"] = Field(
        default="Microsoft.DataFactory/factories/pipelines",
        alias="type",
    )
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )
