from cloe_metadata import base
from cloe_metadata.shared import jobs
from cloe_metadata.utils.templating_engine.general_templates import env

from cloe_etl_adf import factory_objects


def transform_fs2db_to_factory_object(
    job: jobs.FS2DB,
    batchstep: base.Batchstep,
) -> factory_objects.ExecutePipelineActivity:
    """This function can be used to generate the ExecutePipeline activity to call the job pipeline
    in the template adf. It will use the metadata from the fs2db job to generate the parameter values.

    Args:
        job (base.FS2DB): _description_

    Returns:
        factory_objects.ExecutePipelineActivity: _description_
    """
    template = env.get_template("object_identifier.sql.j2")
    schema, table = job.databases.get_table_and_schema(job.sink_table.id)
    parameters = {
        "filePathPattern": job.rendered_folder_path_pattern,
        "fileNamePattern": job.rendered_filename_pattern,
        "datasetName": job.dataset_type.name,
        "tableFQDN": template.render(
            connection=job.base_obj.sink_connection_id,
            schema_obj=schema,
            table_obj=table,
        ),
        "stageName": job.source_connection.name,
        "useFileCatalog": str(job.base_obj.get_from_filecatalog),
    }
    type_properties = factory_objects.ExecutePipelineTypeProperties(
        parameters=parameters,
        pipeline={
            "referenceName": f"job_fs2db_{job.source_connection.name}_{job.sink_connection.name}",
            "type": "PipelineReference",
        },
    )
    return factory_objects.ExecutePipelineActivity(
        name=batchstep.name,
        type_properties=type_properties,
        batchstep_id=batchstep.id,
    )
