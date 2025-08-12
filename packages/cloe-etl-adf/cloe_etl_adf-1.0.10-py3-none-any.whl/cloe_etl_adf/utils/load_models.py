import pathlib
import uuid

from cloe_metadata import base
from cloe_metadata.shared import jobs
from cloe_metadata.utils import model_transformer


def load_models(
    input_model_path: pathlib.Path,
) -> tuple[
    base.Batches,
    dict[uuid.UUID, jobs.DB2FS | jobs.ExecSQL | jobs.FS2DB],
    dict[uuid.UUID, jobs.ExecSQL],
]:
    batches, b_errors = base.Batches.read_instances_from_disk(input_model_path)
    databases, d_errors = base.Databases.read_instances_from_disk(input_model_path)
    connections, c_errors = base.Connections.read_instances_from_disk(input_model_path)
    jobs, j_errors = base.Jobs.read_instances_from_disk(input_model_path)
    data_source_infos, dsi_errors = base.DataSourceInfos.read_instances_from_disk(
        input_model_path,
    )
    tenants, t_errors = base.Tenants.read_instances_from_disk(input_model_path)
    dataset_types, dt_errors = base.DatasetTypes.read_instances_from_disk(
        input_model_path,
    )
    sourcesystems, s_errors = base.Sourcesystems.read_instances_from_disk(
        input_model_path,
    )
    exec_sqls, s_e_errors = model_transformer.transform_exec_sql_to_shared(
        jobs,
        connections=connections,
    )
    (
        shared_data_source_infos,
        s_dsi_errors,
    ) = model_transformer.transform_data_source_info_to_shared(
        data_source_infos,
        sourcesystems=sourcesystems,
        tenants=tenants,
    )
    db2fss, s_db2fs_errors = model_transformer.transform_db2fs_to_shared(
        jobs,
        data_source_infos=shared_data_source_infos,
        dataset_types=dataset_types,
        databases=databases,
        connections=connections,
    )
    fs2dbs, s_fs2db_errors = model_transformer.transform_fs2db_to_shared(
        jobs,
        dataset_types=dataset_types,
        databases=databases,
        connections=connections,
        exec_sqls=exec_sqls,
    )
    jobs_shared_complete = exec_sqls | db2fss | fs2dbs
    if (
        len(b_errors) > 0
        or len(d_errors) > 0
        or len(c_errors) > 0
        or len(j_errors) > 0
        or len(dsi_errors) > 0
        or len(t_errors) > 0
        or len(dt_errors) > 0
        or len(s_errors) > 0
        or len(s_e_errors) > 0
        or len(s_dsi_errors) > 0
        or len(s_db2fs_errors) > 0
        or len(s_fs2db_errors) > 0
    ):
        raise ValueError(
            "The provided models did not pass validation, please run validation.",
        )
    return batches, jobs_shared_complete, exec_sqls
