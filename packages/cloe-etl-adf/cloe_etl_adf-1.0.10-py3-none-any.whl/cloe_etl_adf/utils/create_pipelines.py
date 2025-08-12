import logging
import uuid

from cloe_metadata import base
from cloe_metadata.shared import jobs

from cloe_etl_adf import factory_objects, utils

logger = logging.getLogger(__name__)


def create_master_pipeline(
    master_name: str,
    pipelines: list[factory_objects.PipelineResource],
    folder_name: str,
) -> factory_objects.PipelineResource:
    pipe_activities: list[factory_objects.ExecutePipelineActivity] = []
    for pipeline in pipelines:
        type_properties = factory_objects.ExecutePipelineTypeProperties(
            pipeline={
                "referenceName": pipeline.name,
                "type": "PipelineReference",
            },
        )
        exec_pipe = factory_objects.ExecutePipelineActivity(
            name=f"Execute {pipeline.name}",
            type_properties=type_properties,
        )
        pipe_activities.append(exec_pipe)
    resource_properties = factory_objects.PipelineResourceProperties(
        activities=pipe_activities,
        folder={"name": folder_name},
    )
    return factory_objects.PipelineResource(
        name=master_name,
        properties=resource_properties,
    )


def create_pipelines(
    batches: base.Batches,
    jobs: dict[uuid.UUID, jobs.FS2DB | jobs.DB2FS | jobs.ExecSQL],
) -> tuple[list[factory_objects.PipelineResource], list[factory_objects.Trigger]]:
    pipeline_resources: list[factory_objects.PipelineResource] = []
    used_trigger: list[factory_objects.Trigger] = []
    for batch in batches.batches:
        pipelines: dict[str, factory_objects.PipelineResource] = {}
        (
            folder_root,
            pipeline_names,
            pipeline_build_plan,
            activity_packages,
        ) = utils.prepare_batches_and_jobs(batch, jobs)
        for pipeline_id, pipeline in pipeline_build_plan.items():
            pipe_activities = utils.create_pipeline_activities(
                batch,
                pipeline,
                activity_packages,
            )
            pipeline_property = factory_objects.PipelineResourceProperties(
                activities=pipe_activities,
                folder={"name": f"{folder_root}"},
            )
            full_pipeline = factory_objects.PipelineResource(
                name=pipeline_names[pipeline_id],
                properties=pipeline_property,
            )
            pipelines[str(pipeline_id)] = full_pipeline
            logger.info("Pipeline %s created", pipeline_id)
        if len(pipeline_build_plan) > 1:
            pipeline_master_name = f"{batch.name}_master"
            pipelines["master"] = create_master_pipeline(
                pipeline_master_name,
                list(pipelines.values()),
                folder_root,
            )
            logger.info("Pipeline master created")
            master = pipelines["master"]
            logger.info("Pipeline trigger created")
        else:
            master = list(pipelines.values())[0]
        recurrence = factory_objects.ScheduleTriggerTypeProperties.transform_cron_to_recurrence(
            batch.cron,
            batch.timezone,
        )
        trigger_properties = factory_objects.TriggerProperties(
            pipelines=[
                {
                    "pipelineReference": {
                        "referenceName": master.name,
                        "type": "PipelineReference",
                    },
                },
            ],
            type_properties=factory_objects.ScheduleTriggerTypeProperties(
                recurrence=recurrence,
            ),
        )
        used_trigger.append(
            factory_objects.Trigger(
                name=f"{master.name}_trigger",
                properties=trigger_properties,
            ),
        )

        logger.info("Pipeline trigger created")
        pipeline_resources += list(pipelines.values())
    return pipeline_resources, used_trigger
