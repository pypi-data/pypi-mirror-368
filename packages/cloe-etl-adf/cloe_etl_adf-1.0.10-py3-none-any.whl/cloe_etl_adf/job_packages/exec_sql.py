from cloe_metadata import base
from cloe_metadata.shared import jobs
from cloe_metadata_to_ddl import utils

from cloe_etl_adf import factory_objects


def transform_exec_sql_to_factory_object(
    job: jobs.ExecSQL,
    batchstep: base.Batchstep,
) -> factory_objects.ExecutePipelineActivity:
    """This function can be used to generate the ExecutePipeline activity to call the job pipeline
    in the template adf. It will use the metadata from the exec_sql job to generate the parameter values.

    Args:
        job (model.ExecSQL): _description_

    Returns:
        factory_objects.ExecutePipelineActivity: _description_
    """
    parameters = {
        "sqlQuery": utils.get_procedure_call_with_parameters(
            job,
            {"stuff": "?"},
            escape_quote_params=False,
        ),
    }
    type_properties = factory_objects.ExecutePipelineTypeProperties(
        parameters=parameters,
        pipeline={
            "referenceName": f"job_exec_sql_{job.sink_connection.name}",
            "type": "PipelineReference",
        },
    )
    return factory_objects.ExecutePipelineActivity(
        name=batchstep.name,
        type_properties=type_properties,
        batchstep_id=batchstep.id,
    )
