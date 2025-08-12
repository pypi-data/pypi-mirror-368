from cloe_metadata import base
from cloe_metadata.shared import jobs

from cloe_etl_adf import factory_objects


def transform_db2fs_to_factory_object(
    job: jobs.DB2FS,
    batchstep: base.Batchstep,
) -> factory_objects.ExecutePipelineActivity:
    """This function can be used to generate the ExecutePipeline activity to call the job pipeline
    in the template adf. It will use the metadata from the db2fs job to generate the parameter values.

    Args:
        job (base.DB2FS): _description_

    Returns:
        factory_objects.ExecutePipelineActivity: _description_
    """
    schema, table = job.databases.get_table_and_schema(job.source_table.id)
    parameters: dict[str, str] = {
        "fileNameContent": job.data_source_info.base_obj.content,
        "fileNameSourcesystemName": job.data_source_info.sourcesystem.name,
        "fileNameTenantName": job.data_source_info.tenant.name if job.data_source_info.tenant is not None else "",
        "fileNameObjectDescription": ""
        if job.data_source_info.base_obj.object_description is None
        else job.data_source_info.base_obj.object_description,
        "fileNameDatasetTypeName": job.dataset_type.name,
        "sourceSchemaName": "" if schema is None else schema.name,
        "sourceTableName": "" if table is None else table.name,
        "sourceSelectQuery": job.rendered_select_query,
        "fileFolderPath": job.rendered_folder_path,
        "dataSourceInfoID": str(job.base_obj.datasource_info_id),
        "sourceConnectionID": str(job.base_obj.source_connection_id),
        "sinkConnectionID": str(job.base_obj.sink_connection_id),
        "datasetTypeID": str(job.base_obj.dataset_type_id),
        "fileStorageContainer": job.base_obj.container_name,
    }
    if job.data_source_info.base_obj.content == "delta":
        parameters["sequenceColumnName"] = (
            job.base_obj.sequence_column_name if job.base_obj.sequence_column_name is not None else ""
        )
        parameters["sourceSelectQuery"] = job.rendered_select_query.replace(
            "${adf_delta_artifact}",
            f"{job.base_obj.sequence_column_name} <= '$SEQUENCE_END' $SEQUENCE_START",
        )
    type_properties = factory_objects.ExecutePipelineTypeProperties(
        parameters=parameters,
        pipeline={
            "referenceName": f"job_db2fs_{job.data_source_info.base_obj.content}_{job.source_connection.name}"
            f"_{job.sink_connection.name}",
            "type": "PipelineReference",
        },
    )
    return factory_objects.ExecutePipelineActivity(
        name=batchstep.name,
        type_properties=type_properties,
        batchstep_id=batchstep.id,
    )
