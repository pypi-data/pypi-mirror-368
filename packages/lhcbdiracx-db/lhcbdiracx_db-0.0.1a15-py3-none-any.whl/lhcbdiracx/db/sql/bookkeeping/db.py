from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, cast

import oracledb
from diracx.core.exceptions import InvalidQueryError
from diracx.core.models import SearchSpec, SortSpec
from diracx.db.sql.utils import BaseSQLDB, apply_search_filters, apply_sort_constraints
from pydantic import TypeAdapter
from sqlalchemy import func, select

from lhcbdiracx.core.models import BKSearchParams

from .models import (
    ConfigurationInsert,
    DataTakingConditionInsert,
    FileInsert,
    FileTypeInsert,
    JobInsert,
    ProcessingInsert,
    ProductionContainerInsert,
    ProductionOutputFileInsert,
    SimulationConditionInsert,
    StepInsert,
    StepsContainerInsert,
)
from .queries import standard_dataset_query, standard_files_query
from .schema import Base as BookkeepingDBBase
from .schema import (
    Configuration,
    DataTakingCondition,
    EventType,
    File,
    FileType,
    Job,
    Processing,
    ProductionOutputFile,
    ProductionsContainer,
    SimulationCondition,
    Step,
    StepsContainer,
)

if "ORACLE_INSTANT_CLIENT_HOME" in os.environ:
    oracledb.init_oracle_client(lib_dir=os.environ["ORACLE_INSTANT_CLIENT_HOME"])


def _get_columns(columns, parameters):
    if parameters:
        if unrecognised_parameters := set(parameters) - set(x.name for x in columns):
            raise InvalidQueryError(
                f"Unrecognised parameters requested {unrecognised_parameters}"
            )
        columns = [c for c in columns if c.name in parameters]
    return columns


class BookkeepingDB(BaseSQLDB):
    """Database class for the Bookkeeping database."""

    metadata = BookkeepingDBBase.metadata

    async def hello(self) -> int:
        query = select(func.count()).select_from(Configuration.__table__)
        result = await self.conn.execute(query)
        return cast(int, result.scalar())

    async def insert_steps(self, steps: list[dict[str, Any]]):
        """Insert steps with automatic stepid assignment."""
        return await self._insert_with_auto_id(Step, steps, "stepid", StepInsert)

    async def insert_configuration(self, configurations: list[dict[str, Any]]):
        """Insert configurations with automatic configurationid assignment."""
        return await self._insert_with_auto_id(
            Configuration, configurations, "configurationid", ConfigurationInsert
        )

    async def insert_filetypes(self, filetypes: list[str]):
        """Insert file types with validation for duplicates.

        File types are converted to uppercase and checked for duplicates.
        This method also checks if the file types already exist in the database.
        """
        filetypes = list(map(str.upper, filetypes))
        if len(set(filetypes)) != len(filetypes):
            raise ValueError("Cannot insert duplicate filetypes!")

        default_version = "1"

        # Check if any file types already exist
        existing = (
            select(FileType.name, func.count(FileType.name))
            .filter(
                func.upper(FileType.name).in_(filetypes),
                FileType.version == default_version,
            )
            .group_by(FileType.name)
        )

        result_existing = await self.conn.execute(existing)
        existing_fts = {row.name for row in result_existing}

        if existing_fts:
            raise ValueError(
                f"File type(s) already exist(s): {sorted(list(existing_fts))!r}"
            )

        # Prepare records for insertion
        records_to_insert = [
            {
                "name": ft,
                "version": default_version,
                "description": "",
            }
            for ft in filetypes
        ]

        # Use our common helper for ID assignment and insertion
        return await self._insert_with_auto_id(
            FileType, records_to_insert, "filetypeid", FileTypeInsert
        )

    async def get_processing_passes(self):
        """Get all processing passes from the processing table."""
        return (
            await self.conn.execute(
                select(Processing.id, Processing.name, Processing.parentid)
            )
        ).fetchall()

    async def insert_processing_passes(self, path: list[tuple[str]]):
        """Insert processing passes into the processing table.

        e.g. bookkeeping_db.insert_procesing_pass([
            ["Real Data", "Turbo999", "MyPass"]  # corresponds to /Real Data/Turbo999/MyPass
        ])
        """

        # TODO: extremely crude insert. Will have to be improved by a less racy solution
        last_id = -1

        for pp in path:
            # check if processing pass already exists
            result = (
                await self.conn.execute(
                    select(Processing.id).filter(
                        Processing.name == pp,
                        Processing.parentid == last_id,
                    )
                )
            ).scalar_one_or_none()

            if result:
                # if it does then use it
                last_id = result
            else:
                # otherwise insert it
                next_id = (
                    await self.conn.execute(
                        select(func.coalesce(func.max(Processing.id) + 1, 1))
                    )
                ).scalar_one()

                record = {
                    "id": next_id,
                    "parentid": last_id,
                    "name": pp,
                }

                record = self._validate_records(ProcessingInsert, [record])[0]

                await self.conn.execute(
                    Processing.__table__.insert(),
                    [record],
                )
                last_id = next_id
        return last_id

    async def get_file_types_by_id(
        self, ids: list[int], default_version="1"
    ) -> dict[int, str]:
        result = await self.conn.execute(
            select(FileType.filetypeid, FileType.name).filter(
                FileType.filetypeid.in_(ids),
                FileType.version == default_version,
            )
        )
        return {int(row.filetypeid): row.name for row in result}

    async def dump_all_bk_paths(self):
        """Dump all bookkeeping paths in the bookkeeping database."""

        inner_alias = standard_dataset_query()

        final_query = select(inner_alias.c.BkPath)

        async with self.conn.stream(final_query) as result:
            async for row in result:
                yield row[0]

    async def summary(self, group_by, search) -> list[dict[str, str | int]]:
        """Get a summary of the datasets."""

        if not group_by:
            raise InvalidQueryError("Group by parameters must be provided")

        inner_alias = standard_dataset_query()

        # Alias the inner query so we can reference its columns in the outer query.
        columns = _get_columns(inner_alias.c, group_by)
        stmt = select(*columns, func.count("ConfigName").label("count"))
        stmt = apply_search_filters(inner_alias.c.__getitem__, stmt, search)
        stmt = stmt.group_by(*columns)

        # Execute the query
        return [
            dict(row._mapping)
            async for row in (await self.conn.stream(stmt))
            if row.count > 0  # type: ignore
        ]

    async def search(
        self,
        parameters: list[str] | None,
        search: list[BKSearchParams],
        sorts: list[SortSpec],
        *,
        distinct: bool = False,
        per_page: int = 100,
        page: int | None = None,
    ) -> tuple[int, list[dict[Any, Any]]]:
        """Search for bookkeeping datasets in the database."""
        # Find which columns to select

        inner_alias = standard_dataset_query()
        columns = _get_columns(inner_alias.c, parameters)
        stmt = select(*columns)

        stmt = apply_search_filters(inner_alias.c.__getitem__, stmt, search)
        stmt = apply_sort_constraints(inner_alias.c.__getitem__, stmt, sorts)

        if distinct:
            stmt = stmt.distinct()

        # Calculate total count before applying pagination
        total_count_subquery = stmt.alias()
        total_count_stmt = select(func.count()).select_from(total_count_subquery)
        total = (await self.conn.execute(total_count_stmt)).scalar_one()

        # Apply pagination
        if page is not None:
            if page < 1:
                raise InvalidQueryError("Page must be a positive integer")
            if per_page < 1:
                raise InvalidQueryError("Per page must be a positive integer")
            stmt = stmt.offset((page - 1) * per_page).limit(per_page)

        # Execute the query
        return total, [
            dict(row._mapping) async for row in (await self.conn.stream(stmt))
        ]

    async def search_files(
        self,
        parameters: list[str] | None,
        search: list[SearchSpec],
        sorts: list[SortSpec],
        *,
        distinct: bool = False,
        per_page: int = 100,
        page: int | None = None,
    ) -> tuple[int, list[dict[Any, Any]]]:
        """Search for bookkeeping datasets in the database."""

        async with standard_files_query(self.conn, parameters, search, sorts) as (
            stmt,
            _,
        ):
            if distinct:
                stmt = stmt.distinct()

            # Calculate total count before applying pagination
            total_count_subquery = stmt.alias()
            total_count_stmt = select(func.count()).select_from(total_count_subquery)
            total = (await self.conn.execute(total_count_stmt)).scalar_one()

            # Apply pagination
            if page is not None:
                if page < 1:
                    raise InvalidQueryError("Page must be a positive integer")
                if per_page < 1:
                    raise InvalidQueryError("Per page must be a positive integer")
                stmt = stmt.offset((page - 1) * per_page).limit(per_page)

            return total, [
                dict(row._mapping) async for row in (await self.conn.stream(stmt))
            ]
            # results = [
            #     dict(row._mapping) async for row in (await self.conn.stream(stmt))
            # ]
            # # Group by BkPath
            # return total, {
            #     k: list(v)
            #     for k, v in itertools.groupby(results, key=lambda x: x["BkPath"])
            # }

    async def summary_files(self, group_by, search) -> list[dict[str, str | int]]:
        """Get a summary of the files."""
        if not group_by:
            raise InvalidQueryError("Group by parameters must be provided")

        aggregable_columns = {  # TODO: make configurable and extend
            "count": func.count("FileName").label("count"),
            "size": func.sum("FileSize").label("size"),
            "total_luminosity": func.sum("TotalLuminosity").label("total_luminosity"),
        }

        async with standard_files_query(self.conn, group_by, search, []) as (
            stmt,
            selected_columns,
        ):
            assert len(group_by) == len(
                selected_columns
            ), "Group by columns must match selected columns"
            stmt = select(stmt.alias("files_q"), *aggregable_columns.values())
            stmt = stmt.group_by(*group_by)

            # Execute the query
            return [
                dict(row._mapping)
                async for row in (await self.conn.stream(stmt))
                if row.count > 0  # type: ignore
            ]

    async def insert_simulation_condition(self, conditions: list[dict[str, Any]]):
        """Insert simulation conditions with automatic simid assignment."""
        return await self._insert_with_auto_id(
            SimulationCondition, conditions, "simid", SimulationConditionInsert
        )

    async def insert_data_taking_condition(self, conditions: list[dict[str, Any]]):
        """Insert data taking conditions with automatic daqperiodid assignment."""
        return await self._insert_with_auto_id(
            DataTakingCondition, conditions, "daqperiodid", DataTakingConditionInsert
        )

    async def insert_event_type(self, event_types: list[int]):
        """Insert event types with automatic eventtypeid assignment."""
        if not event_types:
            return

        # Insert event types into the database
        await self.conn.execute(
            EventType.__table__.insert(), [{"eventtypeid": et} for et in event_types]
        )

        return event_types

    async def insert_production_container(self, containers: list[dict[str, Any]]):
        """Insert production containers with automatic production ID assignment."""
        return await self._insert_with_auto_id(
            ProductionsContainer, containers, "production", ProductionContainerInsert
        )

    async def insert_job(self, jobs: list[dict[str, Any]]):
        """Insert jobs with automatic jobid assignment."""
        return await self._insert_with_auto_id(Job, jobs, "jobid", JobInsert)

    async def insert_file(self, files: list[dict[str, Any]]):
        """Insert files with automatic fileid assignment."""
        return await self._insert_with_auto_id(File, files, "fileid", FileInsert)

    async def insert_steps_container(self, containers: list[dict[str, Any]]):
        """Insert steps containers.

        StepsContainer has a composite primary key of (production, stepid),
        so both these values must be provided. This method validates that both
        primary key components are present.
        """
        if not containers:
            return []

        validated_containers = self._validate_records(StepsContainerInsert, containers)

        # Insert containers into the database
        await self.conn.execute(StepsContainer.__table__.insert(), validated_containers)

        return validated_containers

    async def insert_production_output_file(self, output_files: list[dict[str, Any]]):
        """Insert production output files."""
        if not output_files:
            return []

        validated_files = self._validate_records(
            ProductionOutputFileInsert, output_files
        )

        # Insert output files into the database
        await self.conn.execute(
            ProductionOutputFile.__table__.insert(), validated_files
        )

        return validated_files

    def _validate_records(
        self,
        model_class: Any,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Validate records using Pydantic models if available.

        Args:
            model_class: Pydantic model class to use for validation
            records: List of records to validate

        Returns:
            List of validated records as dictionaries

        Raises:
            ValueError: If validation fails and descriptive error messages
        """
        if not records:
            return []

        validated_records = []

        model_class = TypeAdapter(list[model_class])

        validated_records = model_class.validate_python(records)
        validated_records = model_class.dump_python(
            validated_records, exclude_none=True
        )

        return validated_records

    async def _insert_with_auto_id(
        self,
        model_class,
        records: list[dict[str, Any]],
        id_column_name: str,
        pydantic_model_class: Optional[Any] = None,
        return_inserted_ids: bool = True,
    ) -> list[Any]:
        """Generic helper for inserting records with auto-incrementing IDs.

        For records that don't have an ID set, calculate and assign the next available ID.
        This is necessary because Oracle doesn't have autoincrement.

        Args:
            model_class: The SQLAlchemy model class
            records: List of record dictionaries to insert
            id_column_name: The name of the ID column
            pydantic_model_class: Optional Pydantic model class for validation
            return_inserted_ids: Whether to return the IDs of inserted records

        Returns:
            List of the IDs of inserted records if return_inserted_ids is True
        """
        if not records:
            return []

        # Validate records if pydantic_model_class is provided
        if pydantic_model_class is not None:
            records = self._validate_records(pydantic_model_class, records)

        # Calculate the next available ID
        next_id_query = select(
            func.coalesce(func.max(getattr(model_class, id_column_name)) + 1, 1)
        )
        next_id = (await self.conn.execute(next_id_query)).scalar_one()

        # Assign IDs to records that don't have one
        records_to_insert = []
        for i, record in enumerate(records):
            record_copy = record.copy()
            if id_column_name not in record_copy:
                record_copy[id_column_name] = next_id + i
            records_to_insert.append(record_copy)

        # Insert records into the database
        await self.conn.execute(model_class.__table__.insert(), records_to_insert)

        if return_inserted_ids:
            return [record[id_column_name] for record in records_to_insert]
        return []
