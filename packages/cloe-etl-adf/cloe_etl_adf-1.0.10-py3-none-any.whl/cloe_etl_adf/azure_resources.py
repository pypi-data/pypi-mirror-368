import logging
import uuid

from cloe_metadata import base
from cloe_metadata.shared import jobs

from cloe_etl_adf import factory_objects, utils

logger = logging.getLogger(__name__)


def build_factory_orchestration(
    batches: base.Batches,
    jobs: dict[uuid.UUID, jobs.FS2DB | jobs.DB2FS | jobs.ExecSQL],
) -> tuple[
    list[factory_objects.PipelineResource],
    list[factory_objects.Trigger],
]:
    pipelines, triggers = utils.create_pipelines(
        batches,
        jobs,
    )
    logger.info("%s Pipelines created", len(pipelines))
    return pipelines, triggers
