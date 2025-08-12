import logging
import pathlib
from typing import Annotated

import typer
from cloe_metadata.utils import writer
from cloe_metadata_to_ddl import utils as ddl_utils

import cloe_etl_adf.azure_resources as azure_res
from cloe_etl_adf import utils

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def build(
    input_model_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to the CLOE model."),
    ],
    output_arm_path: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to the Azure Data Factory or where it should write the artifacts to.",
        ),
    ],
    output_sql_path: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to output the Stored Procedure scripts for Exec_SQL jobs.",
        ),
    ],
    transaction_based_exec_sql: Annotated[
        bool,
        typer.Option(help="Use pipeline run id and query tags for default monitoring."),
    ] = False,
    activate_monitoring: Annotated[
        bool,
        typer.Option(help="Run each query of ExecSQL jobs in its own transaction."),
    ] = True,
) -> None:
    """
    Builds the Azure Data Factory orchestration pipelines for all CLOE batches.
    Will then write it to disk. The used format
    is equivalent to the one used by the Azure Data Factory by default in git.
    """
    batches, jobs_shared_complete, exec_sqls = utils.load_models(
        input_model_path=input_model_path,
    )
    pipelines, triggers = azure_res.build_factory_orchestration(
        batches,
        jobs_shared_complete,
    )
    sql_procedures = ddl_utils.create_stored_procedure_script(
        list(exec_sqls.values()),
        transaction_based_exec_sql,
        activate_monitoring,
    )
    logger.info("Stored procedures created")
    for pipeline in pipelines:
        writer.write_string_to_disk(
            pipeline.model_dump_json(indent=4, by_alias=True, exclude_none=True),
            output_arm_path / "pipeline" / f"{pipeline.name}.json",
        )
    for trigger in triggers:
        writer.write_string_to_disk(
            trigger.model_dump_json(indent=4, by_alias=True, exclude_none=True),
            output_arm_path / "trigger" / f"{trigger.name}.json",
        )
    for k, v in sql_procedures.items():
        writer.write_string_to_disk(v, output_sql_path / f"stored_procedures{k}.sql")
