from __future__ import annotations

import logging
import uuid
from typing import Literal

from cloe_metadata.utils import writer
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

logger = logging.getLogger(__name__)


class ActivityUserProperties(BaseModel):
    batch_id: int
    batchstep_id: uuid.UUID
    job_id: uuid.UUID
    job_name: str
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )

    def _get_user_properties(self) -> list[dict[str, str]]:
        return [
            {"name": "batch_id", "value": str(self.batch_id)},
            {"name": "batchstep_id", "value": str(self.batchstep_id)},
            {"name": "job_id", "value": str(self.job_id)},
            {"name": "job_name", "value": str(self.job_name)},
        ]


class ActivityDependency(BaseModel):
    activity: str
    dependency_conditions: list[Literal["Succeeded", "Completed"]]
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )


class ExecutePipelineTypeProperties(BaseModel):
    pipeline: dict[str, str]
    wait_on_completion: bool = True
    parameters: dict[str, str] = {}
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )


class ExecutePipelineActivity(BaseModel):
    batchstep_id: uuid.UUID | None = Field(default=None, exclude=True)
    name: str
    description: str = ""
    depends_on: list[ActivityDependency] = []
    pipeline_variables: list[str] = Field(default=[], exclude=True)
    user_properties: list[ActivityUserProperties] = []
    arm_type: Literal["ExecutePipeline"] = Field(
        default="ExecutePipeline",
        alias="type",
    )
    type_properties: ExecutePipelineTypeProperties
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=writer.to_lower_camel_case,
    )

    @field_validator("name")
    @classmethod
    def catalog_name_template(cls, value: str, info: ValidationInfo) -> str:
        batchstep_id: uuid.UUID = info.data.get("batchstep_id", uuid.UUID(int=0))
        if len(value) > 55:
            logger.warning(
                ("Length of activity name %s is %s but must not exceed 55." " It was shortened."),
                value,
                len(value),
            )
            value = f"{value[0:46]}{str(batchstep_id).split('-')[0]}"
        return value


ActivityDependency.model_rebuild()
