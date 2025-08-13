from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from enum import StrEnum

from diracx.core.exceptions import InvalidQueryError
from diracx.core.models import (
    ScalarSearchOperator,
    SearchSpec,
    SortSpec,
    VectorSearchOperator,
)
from diracx.db.sql.utils import apply_search_filters, apply_sort_constraints
from sqlalchemy import literal, null, or_, select

from .bk_types import GotReplicaYes
from .functions import format_as_char
from .schema import (
    Configuration,
    DataQuality,
    DataTakingCondition,
    EventType,
    File,
    FileType,
    Job,
    Processing,
    ProductionOutputFile,
    ProductionsContainer,
    SimulationCondition,
    TempQueryFileTypeName,
    TempQueryProductionIds,
    clear_temp_tables,
)


class JoinType(StrEnum):
    """Enum for different types of joins available in the bookkeeping queries."""

    JOBS = "JOBS"
    PRODUCTIONSCONTAINER = "PRODUCTIONSCONTAINER"
    CONFIGURATIONS = "CONFIGURATIONS"
    FILETYPES = "FILETYPES"
    DATAQUALITY = "DATAQUALITY"
    CONDESC = "CONDESC"
    PROCPATHS = "PROCPATHS"
    RUNS = "RUNS"
    SMOG2STATE = "SMOG2STATE"
    TMP_PRODUCTION = "TMP_PRODUCTION"
    TMP_FILETYPES = "TMP_FILETYPES"


def _get_columns(column_names, parameter_names, mapping):
    if parameter_names:
        if unrecognised_parameters := set(parameter_names) - set(
            x for x in column_names
        ):
            raise InvalidQueryError(
                f"Unrecognised parameters requested {unrecognised_parameters}"
            )
        columns = [
            (mapping[c][0].label(c), mapping[c][1])
            for c in column_names
            if c in parameter_names
        ]
    else:
        columns = [(mapping[c][0].label(c), mapping[c][1]) for c in column_names]

    return columns


def standard_dataset_query():
    """Standard query to get dataset information from the Bookkeeping."""
    procpaths_cte = processing_path_cte()
    condesc_cte = conditions_description_cte()

    inner_query = (
        select(
            Configuration.configname.label("ConfigName"),
            Configuration.configversion.label("ConfigVersion"),
            condesc_cte.c.description.label("ConditionsDescription"),
            procpaths_cte.c.procpath.label("ProcPath"),
            EventType.eventtypeid.label("EventType"),
            FileType.name.label("FileType"),
            (
                "/"
                + Configuration.configname
                + "/"
                + Configuration.configversion
                + "/"
                + condesc_cte.c.description
                + "/"
                + procpaths_cte.c.procpath
                + "/"
                + format_as_char(EventType.eventtypeid)
                + "/"
                + FileType.name
            ).label("BkPath"),
        )
        .select_from(ProductionsContainer)
        .join(
            Configuration,
            ProductionsContainer.configurationid == Configuration.configurationid,
        )
        .join(
            condesc_cte,
            or_(
                condesc_cte.c.daqid == ProductionsContainer.daqperiodid,
                condesc_cte.c.simid == ProductionsContainer.simid,
            ),
        )
        .join(procpaths_cte, ProductionsContainer.processingid == procpaths_cte.c.id)
        .join(
            ProductionOutputFile,
            ProductionOutputFile.production == ProductionsContainer.production,
        )
        .join(FileType, ProductionOutputFile.filetypeid == FileType.filetypeid)
        .join(EventType, EventType.eventtypeid == ProductionOutputFile.eventtypeid)
        .where(
            ProductionOutputFile.visible == "Y",
            ProductionOutputFile.gotreplica == GotReplicaYes,
        )
        .distinct()
    )

    inner_alias = inner_query.alias("inner_q")
    return inner_alias


def processing_path_cte():
    # Base case: select root rows (where parentid is None) with procpath equal to name.
    base = select(Processing.id, Processing.name.label("procpath")).where(
        or_(Processing.parentid.is_(None), Processing.parentid == -1)
    )

    # Create a recursive CTE named "procpaths"
    procpaths_cte = base.cte("procpaths", recursive=True)

    # Recursive step: join child rows and append their names to the parent's procpath.
    recursive = select(
        Processing.id,
        (procpaths_cte.c.procpath + literal("/") + Processing.name).label("procpath"),
    ).where(Processing.parentid == procpaths_cte.c.id)

    # Union the base and recursive part.
    procpaths_cte = procpaths_cte.union_all(recursive)

    return procpaths_cte


def conditions_description_cte():
    data_taking_query = select(
        DataTakingCondition.daqperiodid.label("daqid"),
        null().label("simid"),
        DataTakingCondition.description.label("description"),
    ).distinct()
    simulation_query = select(
        null().label("daqid"),
        SimulationCondition.simid.label("simid"),
        SimulationCondition.simdescription.label("description"),
    ).distinct()

    condesc_union = data_taking_query.union(simulation_query)
    condesc_cte = condesc_union.cte("condesc")

    return condesc_cte


class TableJoins(set):
    """Helper for managing table joins in queries, with ordering."""

    _order = [
        JoinType.JOBS,
        JoinType.PRODUCTIONSCONTAINER,
        JoinType.CONFIGURATIONS,
        JoinType.FILETYPES,
        JoinType.DATAQUALITY,
        JoinType.CONDESC,
        JoinType.PROCPATHS,
        JoinType.RUNS,
        JoinType.SMOG2STATE,
        JoinType.TMP_PRODUCTION,
        JoinType.TMP_FILETYPES,
    ]

    def __init__(self):
        super().__init__()
        self.temp_table_touched = False

    def extend(self, iterable):
        for x in iterable:
            self.add(x)

    async def add_temp_table_join(
        self, join: JoinType, conn, values: str | int | list[str | int]
    ):
        """Add a temporary table join with values."""

        if join not in (JoinType.TMP_PRODUCTION, JoinType.TMP_FILETYPES):
            raise ValueError(f"Invalid join type for temporary table: {join}")

        if isinstance(values, (str, int)):
            values = [values]

        temp_table = None

        if join == JoinType.TMP_PRODUCTION:
            temp_table = TempQueryProductionIds.__table__
        elif join == JoinType.TMP_FILETYPES:
            temp_table = TempQueryFileTypeName.__table__
        else:
            raise ValueError(f"Unsupported temporary table join: {join}")

        self.temp_table_touched = True
        self.add(join)

        cname = temp_table.columns.keys()[0]  # Get the first column name
        await conn.execute(temp_table.insert(), [{cname: v} for v in values])

    def apply_joins_to(
        self,
        query,
        condesc_cte,
        procpaths_cte,
    ):
        """
        Apply the joins to the query based on the set of join types.

        The joins are applied in the order defined in self._order.
        If a join type is not recognized, it raises a ValueError.

        Args:
            query: The SQLAlchemy query object to which joins will be applied.

        Returns:
            The modified query with the appropriate joins applied.
        Raises:
            ValueError: If an unknown join type is encountered.
        """

        mapping = {
            JoinType.JOBS: (
                Job,
                (File.jobid == Job.jobid) & (File.production == Job.production),
            ),
            JoinType.PRODUCTIONSCONTAINER: (
                ProductionsContainer,
                File.production == ProductionsContainer.production,
            ),
            JoinType.CONFIGURATIONS: (
                Configuration,
                ProductionsContainer.configurationid == Configuration.configurationid,
            ),
            JoinType.FILETYPES: (FileType, File.filetypeid == FileType.filetypeid),
            JoinType.DATAQUALITY: (
                DataQuality,
                File.qualityid == DataQuality.qualityid,
            ),
            JoinType.CONDESC: (
                condesc_cte,
                (ProductionsContainer.simid == condesc_cte.c.simid)
                | (ProductionsContainer.daqperiodid == condesc_cte.c.daqid),
            ),
            JoinType.PROCPATHS: (
                procpaths_cte,
                procpaths_cte.c.id == ProductionsContainer.processingid,
            ),
            JoinType.TMP_FILETYPES: (
                TempQueryFileTypeName,
                FileType.name == TempQueryFileTypeName.name,
            ),
            JoinType.TMP_PRODUCTION: (
                TempQueryProductionIds,
                File.production == TempQueryProductionIds.productionid,
            ),
        }

        # Apply joins in the defined order
        ordered_joins = sorted(
            self,
            key=lambda x: self._order.index(x) if x in self._order else sys.maxsize,
        )
        for join_type in ordered_joins:
            if join_type in mapping:
                table, condition = mapping[join_type]
                query = query.join(table, condition)
            else:
                raise ValueError(f"Unknown or improperly configured join: {join_type}")
        return query

    @classmethod
    def sort_key(cls, value: JoinType) -> int:
        try:
            return cls._order.index(value)
        except ValueError:
            return sys.maxsize


@asynccontextmanager
async def standard_files_query(
    conn,
    parameters: list | None = None,
    search: list[SearchSpec] | None = None,
    sorts: list[SortSpec] | None = None,
):
    """Standard query to get file information from the Bookkeeping."""

    condesc_cte = conditions_description_cte()
    proc_path_cte = processing_path_cte()

    # Define all selectable columns and their joins if applicable

    selectable_columns_and_joins = {
        "BkPath": (
            (
                "/"
                + Configuration.configname
                + "/"
                + Configuration.configversion
                + "/"
                + condesc_cte.c.description
                + "/"
                + proc_path_cte.c.procpath
                + "/"
                + format_as_char(File.eventtypeid)
                + "/"
                + FileType.name
            ),
            [
                JoinType.CONFIGURATIONS,
                JoinType.PRODUCTIONSCONTAINER,
                JoinType.CONDESC,
                JoinType.PROCPATHS,
                JoinType.FILETYPES,
            ],
        ),
        "FileID": (File.fileid, []),
        "FileName": (File.filename, []),
        "FileSize": (File.filesize, []),
        "FileTypeID": (File.filetypeid, []),
        "CreationDate": (File.creationdate, []),
        "EventStat": (File.eventstat, []),
        "Adler32": (File.adler32, []),
        "MD5Sum": (File.md5sum, []),
        "GUID": (File.guid, []),
        "JobID": (File.jobid, []),
        "ProductionID": (
            File.production,
            [JoinType.PRODUCTIONSCONTAINER],
        ),  # JoinType.TMP_PRODUCTION if searching by production
        "ConfigName": (
            Configuration.configname,
            [JoinType.CONFIGURATIONS, JoinType.PRODUCTIONSCONTAINER],
        ),
        "ConfigVersion": (
            Configuration.configversion,
            [JoinType.CONFIGURATIONS, JoinType.PRODUCTIONSCONTAINER],
        ),
        "ConditionsDescription": (
            condesc_cte.c.description,
            [JoinType.CONDESC, JoinType.PRODUCTIONSCONTAINER],
        ),
        "TCKs": (Job.tck, [JoinType.JOBS]),
        "ProcPath": (
            proc_path_cte.c.procpath,
            [JoinType.PRODUCTIONSCONTAINER, JoinType.PROCPATHS],
        ),
        "FileType": (
            FileType.name,
            [JoinType.FILETYPES],  # JoinType.TMP_FILETYPES if searching by filetype
        ),
        "RunNumber": (Job.runnumber, [JoinType.JOBS]),
        "EventType": (File.eventtypeid, []),
        "InsertTimestamp": (File.inserttimestamp, []),
        "JobStart": (Job.jobstart, [JoinType.JOBS]),
        "JobEnd": (Job.jobend, [JoinType.JOBS]),
        "GotReplica": (File.gotreplica, []),
        "VisibilityFlag": (File.visibilityflag, []),
        "FullStat": (File.fullstat, []),
        "PhysicsStat": (File.physicstat, []),
        "Luminosity": (File.luminosity, []),
        "InstLuminosity": (File.instluminosity, []),
        # TODO: Smog2 states, Data quality, ExtendedDQOK
        # "DataQualityID": (File.qualityid, [JoinType.DATAQUALITY]),
    }

    # Aggregate join dependencies

    joins = TableJoins()

    columns_selected, joins_parameters = zip(
        *_get_columns(
            selectable_columns_and_joins.keys(),
            parameters,
            selectable_columns_and_joins,
        )
    )
    for js in joins_parameters:
        if js:
            joins.extend(js)

    try:
        for search_spec in search or []:
            if search_spec["parameter"] not in selectable_columns_and_joins:
                raise InvalidQueryError(
                    f"Search parameter {search_spec['parameter']=} is not supported in this query."
                )

            for join in selectable_columns_and_joins[search_spec["parameter"]][1]:
                joins.add(join)

            if search_spec["parameter"] in ("ProductionID", "FileType"):
                join_values = None
                if search_spec["operator"] == VectorSearchOperator.IN:
                    join_values = search_spec["values"]

                elif search_spec["operator"] == ScalarSearchOperator.EQUAL:
                    join_values = [search_spec["value"]]
                else:
                    raise InvalidQueryError(
                        f"Search operator {search_spec['operator']} is not supported for temporary table joins."
                    )

                if search_spec["parameter"] == "ProductionID":
                    await joins.add_temp_table_join(
                        JoinType.TMP_PRODUCTION, conn, values=join_values
                    )
                elif search_spec["parameter"] == "FileType":
                    await joins.add_temp_table_join(
                        JoinType.TMP_FILETYPES, conn, values=join_values
                    )

        query = select(*columns_selected).select_from(File)
        query = joins.apply_joins_to(query, condesc_cte, proc_path_cte)

        # Create a mapping function for the columns before applying filters/sorts
        # We need to map parameters to the actual column objects from the joined tables
        def column_mapper(parameter_name):
            # Map the parameter name to the actual column from our selectable_columns_and_joins
            if parameter_name in selectable_columns_and_joins:
                return selectable_columns_and_joins[parameter_name][0]
            else:
                raise KeyError(f"Unknown parameter: {parameter_name}")

        query = apply_search_filters(column_mapper, query, search or [])
        query = apply_sort_constraints(column_mapper, query, sorts or [])

        yield query, columns_selected
    finally:
        # Clean up temporary tables if they were used
        if joins.temp_table_touched:
            await clear_temp_tables(conn)
