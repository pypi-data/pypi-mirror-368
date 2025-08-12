import logging
import uuid
from typing import Literal

from cloe_metadata import base
from cloe_metadata.shared import jobs

import cloe_etl_adf.utils as utils
from cloe_etl_adf import factory_objects, job_packages

logger = logging.getLogger(__name__)


def transform_metadata_to_activites(
    job: jobs.FS2DB | jobs.DB2FS | jobs.ExecSQL,
    batchstep: base.Batchstep,
) -> factory_objects.ExecutePipelineActivity:
    if isinstance(job, jobs.DB2FS):
        return job_packages.transform_db2fs_to_factory_object(job, batchstep)
    if isinstance(job, jobs.FS2DB):
        return job_packages.transform_fs2db_to_factory_object(job, batchstep)
    if isinstance(job, jobs.ExecSQL):
        return job_packages.transform_exec_sql_to_factory_object(job, batchstep)
    raise NotImplementedError("Job not implemented.")


def prepare_batches_and_jobs(
    batch: base.Batch,
    jobs: dict[uuid.UUID, jobs.FS2DB | jobs.DB2FS | jobs.ExecSQL],
) -> tuple[
    str,
    dict[int, str],
    dict[int, list[uuid.UUID]],
    dict[
        uuid.UUID,
        factory_objects.ExecutePipelineActivity,
    ],
]:
    activity_packages: dict[
        uuid.UUID,
        factory_objects.ExecutePipelineActivity,
    ] = {}
    folder_root = f"{batch.name}"
    batchstep_to_job_id = {i.id: i.job_id for i in batch.batchsteps}
    for batchstep in batch.batchsteps:
        activity_packages[batchstep.id] = transform_metadata_to_activites(
            jobs[batchstep_to_job_id[batchstep.id]],
            batchstep,
        )
    pipeline_build_plan = utils.optimize_batch(batch.batchsteps)
    pipeline_names = {i: f"{batch.name}_orchestrator_{i}" for i in pipeline_build_plan}
    return folder_root, pipeline_names, pipeline_build_plan, activity_packages


def create_pipeline_activities(
    batch: base.Batch,
    pipeline: list[uuid.UUID],
    activity_packages: dict[
        uuid.UUID,
        factory_objects.ExecutePipelineActivity,
    ],
) -> list[factory_objects.ExecutePipelineActivity]:
    pipe_activities: list[factory_objects.ExecutePipelineActivity] = []
    for batchstep_id in pipeline:
        exec_pipeline = activity_packages[batchstep_id]
        batchstep_deps = batch.get_batchsteps()[batchstep_id].dependencies
        batchstep_deps = [] if batchstep_deps is None else batchstep_deps
        for batchstep_dep in batchstep_deps:
            dep_execute_pipeline = activity_packages[batchstep_dep.dependent_on_batchstep_id]
            condition: Literal["Completed", "Succeeded"] = (
                "Completed" if batchstep_dep.ignore_dependency_failed_state else "Succeeded"
            )
            act_dep = factory_objects.ActivityDependency(
                activity=dep_execute_pipeline.name,
                dependency_conditions=[condition],
            )
            exec_pipeline.depends_on.append(act_dep)
        pipe_activities.append(exec_pipeline)
        logger.debug("Pipeline step %s created", batchstep_id)
    return pipe_activities
