from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
    event,
    text,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column

from .bk_types import (
    BooleanType,
    DoubleType,
    FileTypesArrayType,
    GotReplicaDefault,
    GotReplicaType,
    NumberType,
    StringType,
    TimestampType,
)
from .functions import boolean_type_default, timestamp_now_default


class Base(DeclarativeBase):
    pass


class Configuration(Base):
    __tablename__ = "configurations"

    configurationid = mapped_column(NumberType, primary_key=True)
    configname = mapped_column(StringType(128), nullable=False)
    configversion = mapped_column(StringType(128), nullable=False)

    __table_args__ = (
        UniqueConstraint("configname", "configversion", name="configuration_uk"),
    )


class Tag(Base):
    __tablename__ = "tags"
    tagid = mapped_column(NumberType, primary_key=True)
    name = mapped_column(StringType(256))
    tag = mapped_column(StringType(256))
    inserttimestamp = mapped_column(
        TimestampType, server_default=timestamp_now_default(oracle_stmt="systimestamp")
    )


class Processing(Base):
    __tablename__ = "processing"
    id = mapped_column(NumberType, primary_key=True)
    parentid = mapped_column(NumberType)
    name = mapped_column(StringType(256))
    __table_args__ = (
        Index("processing_pid", "parentid"),
        Index("processing_pid_name", "parentid", "name"),
    )


class FileType(Base):
    __tablename__ = "filetypes"
    filetypeid = mapped_column(NumberType, primary_key=True)
    description = mapped_column(StringType(256))
    name = mapped_column(StringType(64))
    version = mapped_column(StringType(256))
    __table_args__ = (
        UniqueConstraint("name", "version", name="filetypes_name_version"),
        # TODO: this constraint is SPURIOUS! should be removed
        UniqueConstraint("filetypeid", "name", name="filetypes_id_name_uk"),
    )


class Application(Base):
    __tablename__ = "applications"
    applicationid = mapped_column(NumberType, primary_key=True)
    applicationname = mapped_column(StringType(128), nullable=False)
    applicationversion = mapped_column(StringType(128), nullable=False)
    optionfiles = mapped_column(StringType(4000))
    dddb = mapped_column(StringType(256))
    conddb = mapped_column(StringType(256))
    extrapackages = mapped_column(StringType(256))


class DataTakingCondition(Base):
    __tablename__ = "data_taking_conditions"
    daqperiodid = mapped_column(NumberType, primary_key=True)
    description = mapped_column(StringType(256))
    beamcond = mapped_column(StringType(256))
    beamenergy = mapped_column(StringType(256))
    magneticfield = mapped_column(StringType(256))
    velo = mapped_column(StringType(256))
    it = mapped_column(StringType(256))
    tt = mapped_column(StringType(256))
    ot = mapped_column(StringType(256))
    rich1 = mapped_column(StringType(256))
    rich2 = mapped_column(StringType(256))
    spd_prs = mapped_column(StringType(256))
    ecal = mapped_column(StringType(256))
    hcal = mapped_column(StringType(256))
    muon = mapped_column(StringType(256))
    l0 = mapped_column(StringType(256))
    hlt = mapped_column(StringType(256))
    veloposition = mapped_column(StringType(255))
    __table_args__ = (
        Index("data_taking_condition_id_desc", "daqperiodid", "description"),
    )


class DataQuality(Base):
    __tablename__ = "dataquality"
    qualityid = mapped_column(NumberType, primary_key=True)
    dataqualityflag = mapped_column(StringType(256))


class ExtendedDQOK(Base):
    __tablename__ = "extendeddqok"
    runnumber = mapped_column(NumberType, primary_key=True)
    systemname = mapped_column(StringType(64), primary_key=True)


class Smog2(Base):
    __tablename__ = "smog2"
    id = mapped_column(NumberType, primary_key=True)
    state = mapped_column(StringType(64))


class Run(Base):
    __tablename__ = "runs"
    runnumber = mapped_column(NumberType, primary_key=True)
    smog2_id = mapped_column(
        NumberType, ForeignKey("smog2.id", name="fk_runs_smog2_id")
    )
    __table_args__ = (Index("runs_smog2_id", "smog2_id"),)


class EventType(Base):
    __tablename__ = "eventtypes"
    eventtypeid = mapped_column(NumberType, primary_key=True)
    description = mapped_column(StringType(256))
    # "PRIMARY" is a reserved word so we map it to a different Python attribute name:
    primary_value = mapped_column("PRIMARY", StringType(256))


class SimulationCondition(Base):
    __tablename__ = "simulationconditions"
    simid = mapped_column(NumberType, primary_key=True)
    simdescription = mapped_column(StringType(256))
    beamcond = mapped_column(StringType(256))
    beamenergy = mapped_column(StringType(256))
    generator = mapped_column(StringType(256))
    magneticfield = mapped_column(StringType(256))
    detectorcond = mapped_column(StringType(256))
    luminosity = mapped_column(StringType(256))
    g4settings = mapped_column(StringType(256), server_default=text("' '"))
    visible = mapped_column(BooleanType, server_default=boolean_type_default(True))
    inserttimestamps = mapped_column(
        TimestampType, server_default=timestamp_now_default()
    )
    __table_args__ = (
        CheckConstraint("visible IN ('N','Y')", name="simcond_visible_check"),
        UniqueConstraint("simdescription", name="simdesc"),
    )


class ProductionsContainer(Base):
    __tablename__ = "productionscontainer"
    production = mapped_column(NumberType, primary_key=True)
    processingid = mapped_column(
        NumberType, ForeignKey("processing.id", name="fk_productionscontainer_proc")
    )
    simid = mapped_column(
        NumberType,
        ForeignKey("simulationconditions.simid", name="fk1_productionscontainer"),
    )
    daqperiodid = mapped_column(
        NumberType,
        ForeignKey(
            "data_taking_conditions.daqperiodid", name="fk2_productionscontainer"
        ),
    )
    totalprocessing = mapped_column(StringType(256))
    configurationid = mapped_column(
        NumberType, ForeignKey("configurations.configurationid")
    )
    __table_args__ = (
        Index("prodcontdaq", "daqperiodid", "production"),
        Index("prodcontpsim", "simid", "production"),
        Index("prodcont_proc", "processingid"),
        Index("prodcont_proc_prod", "processingid", "production"),
    )


class Step(Base):
    __tablename__ = "steps"
    stepid = mapped_column(NumberType, primary_key=True)
    stepname = mapped_column(StringType(256))
    applicationname = mapped_column(StringType(128), nullable=False)
    applicationversion = mapped_column(StringType(128), nullable=False)
    optionfiles = mapped_column(StringType(4000))
    dddb = mapped_column(StringType(256))
    conddb = mapped_column(StringType(256))
    extrapackages = mapped_column(StringType(256))
    inserttimestamps = mapped_column(
        TimestampType, server_default=timestamp_now_default()
    )
    visible = mapped_column(BooleanType, server_default=boolean_type_default(True))
    inputfiletypes = mapped_column(FileTypesArrayType)
    outputfiletypes = mapped_column(FileTypesArrayType)
    processingpass = mapped_column(StringType(256), nullable=False)
    usable = mapped_column(StringType(10), server_default=text("'Not ready'"))
    dqtag = mapped_column(StringType(256))
    optionsformat = mapped_column(StringType(30))
    ismulticore = mapped_column(BooleanType, server_default=boolean_type_default(False))
    systemconfig = mapped_column(StringType(256))
    mctck = mapped_column(StringType(256))
    __table_args__ = (
        CheckConstraint("visible IN ('N','Y')", name="steps_visible_check"),
        CheckConstraint(
            "usable IN ('Yes', 'Not ready', 'Obsolete')", name="steps_usable_check"
        ),
        CheckConstraint("ismulticore IN ('N','Y')", name="steps_ismulticore_check"),
    )


class StepsContainer(Base):
    __tablename__ = "stepscontainer"
    production = mapped_column(NumberType, primary_key=True)
    stepid = mapped_column(
        NumberType,
        ForeignKey("steps.stepid", name="fk_stepcontainer"),
        primary_key=True,
    )
    step = mapped_column(NumberType)
    eventtypeid = mapped_column(
        NumberType,
        ForeignKey("eventtypes.eventtypeid", name="fk_stepscontainer_eventtypeid"),
    )
    __table_args__ = (Index("steps_id", "stepid"),)


class Job(Base):
    __tablename__ = "jobs"
    jobid = mapped_column(NumberType, primary_key=True)
    configurationid = mapped_column(
        NumberType, ForeignKey("configurations.configurationid", name="jobs_fk1")
    )
    diracjobid = mapped_column(NumberType)
    diracversion = mapped_column(StringType(256))
    eventinputstat = mapped_column(NumberType)
    exectime = mapped_column(DoubleType)
    firsteventnumber = mapped_column(NumberType)
    geometryversion = mapped_column(StringType(256))
    gridjobid = mapped_column(StringType(256))
    jobend = mapped_column(TimestampType)
    jobstart = mapped_column(TimestampType)
    localjobid = mapped_column(StringType(256))
    LOCATION = mapped_column(StringType(256))
    name = mapped_column(StringType(256), unique=True)
    numberofevents = mapped_column(NumberType)
    production = mapped_column(
        NumberType,
        ForeignKey("productionscontainer.production", name="fk_prodcont_prod"),
    )
    programname = mapped_column(StringType(256))
    programversion = mapped_column(StringType(256))
    statisticsrequested = mapped_column(NumberType)
    wncpupower = mapped_column(StringType(256))
    cputime = mapped_column(DoubleType)
    wncache = mapped_column(StringType(256))
    wnmemory = mapped_column(StringType(256))
    wnmodel = mapped_column(StringType(256))
    workernode = mapped_column(StringType(256))
    generator = mapped_column(StringType(256))
    runnumber = mapped_column(NumberType)
    fillnumber = mapped_column(NumberType)
    wncpuhs06 = mapped_column(DoubleType, server_default=text("0.0"))
    totalluminosity = mapped_column(NumberType, server_default=text("0"))
    tck = mapped_column(StringType(20), server_default=text("'None'"))
    stepid = mapped_column(
        NumberType, ForeignKey("steps.stepid", name="fk_jobs_stepid")
    )
    wnmjfhs06 = mapped_column(DoubleType)
    hlt2tck = mapped_column(StringType(20))
    numberofprocessors = mapped_column(NumberType, server_default=text("1"))
    __table_args__ = (
        UniqueConstraint("name", name="job_name_unique"),
        Index("conf_job_run", "configurationid", "jobid", "runnumber"),
        Index("jobsprognameandversion", "programname", "programversion"),
        Index("jobs_diracjobid_jobid", "diracjobid", "jobid"),
        Index("jobs_fill_runnumber", "fillnumber", "runnumber"),
        Index("jobs_productionid", "production"),
        Index("jobs_prod_config_jobid", "production", "configurationid", "jobid"),
        Index("prod_start_end", "production", "jobstart", "jobend"),
        Index("runnumber", "runnumber"),
    )


class File(Base):
    __tablename__ = "files"
    fileid = mapped_column(NumberType, primary_key=True)
    adler32 = mapped_column(StringType(256))
    creationdate = mapped_column(TimestampType)
    eventstat = mapped_column(NumberType)
    eventtypeid = mapped_column(
        NumberType, ForeignKey("eventtypes.eventtypeid", name="files_fk11")
    )
    filename = mapped_column(StringType(256), nullable=False, unique=True)
    filetypeid = mapped_column(
        NumberType, ForeignKey("filetypes.filetypeid", name="files_fk21")
    )
    gotreplica = mapped_column(GotReplicaType, server_default=GotReplicaDefault(False))
    guid = mapped_column(StringType(256), nullable=False)
    jobid = mapped_column(
        NumberType,
        ForeignKey("jobs.jobid", ondelete="CASCADE", name="files_fk31"),
    )
    md5sum = mapped_column(StringType(256), nullable=False)
    filesize = mapped_column(NumberType, server_default=text("0"))
    qualityid = mapped_column(
        NumberType,
        ForeignKey("dataquality.qualityid", name="fk_qualityid"),
        server_default=text("1"),
    )
    inserttimestamp = mapped_column(
        TimestampType,
        nullable=False,
        server_default=timestamp_now_default(oracle_stmt="CURRENT_TIMESTAMP"),
    )
    fullstat = mapped_column(NumberType)
    physicstat = mapped_column(NumberType)
    luminosity = mapped_column(NumberType, server_default=text("0"))
    visibilityflag = mapped_column(
        BooleanType, server_default=boolean_type_default(True)
    )
    instluminosity = mapped_column(NumberType, server_default=text("0"))
    production = mapped_column(
        NumberType,
        ForeignKey("productionscontainer.production", name="fk_files_production"),
        nullable=False,
    )
    __table_args__ = (
        # Check constraints
        CheckConstraint("physicstat < 0", name="check_physicstat"),
        CheckConstraint("visibilityflag IN ('N', 'Y')", name="visibilityflag_check"),
        CheckConstraint("production IS NOT NULL", name="chk_production_not_null"),
        # Indices
        Index("files_filetypeid", "filetypeid"),
        Index("files_guid", "guid"),
        Index("files_job_event_filetype", "jobid", "eventtypeid", "filetypeid"),
        Index("files_time_gotreplica", "inserttimestamp", "gotreplica"),
        Index("f_gotreplica", "gotreplica", "visibilityflag", "jobid"),
        Index(
            "idx_files_got_vis_prod_type",
            "production",
            "gotreplica",
            "visibilityflag",
            "filetypeid",
            "eventtypeid",
        ),
    )


class InputFile(Base):
    __tablename__ = "inputfiles"
    fileid = mapped_column(
        NumberType, ForeignKey("files.fileid", name="files_fk1"), primary_key=True
    )
    jobid = mapped_column(
        NumberType,
        ForeignKey("jobs.jobid", ondelete="CASCADE", name="inputfiles_fk31"),
        primary_key=True,
    )
    __table_args__ = (Index("inputfiles_jobid_test", "jobid", "fileid"),)


class NewRunQuality(Base):
    __tablename__ = "newrunquality"
    runnumber = mapped_column(NumberType, primary_key=True)
    processingid = mapped_column(
        NumberType, ForeignKey("processing.id", name="processing_id"), primary_key=True
    )
    qualityid = mapped_column(
        NumberType, ForeignKey("dataquality.qualityid", name="fk_qualityid_run")
    )
    __table_args__ = (Index("newrunquality_proc", "processingid"),)


class ProductionOutputFile(Base):
    __tablename__ = "productionoutputfiles"
    production = mapped_column(
        NumberType,
        ForeignKey("productionscontainer.production", ondelete="CASCADE"),
        primary_key=True,
    )
    stepid = mapped_column(NumberType, ForeignKey("steps.stepid"), primary_key=True)
    eventtypeid = mapped_column(
        NumberType, ForeignKey("eventtypes.eventtypeid"), primary_key=True
    )
    filetypeid = mapped_column(
        NumberType, ForeignKey("filetypes.filetypeid"), primary_key=True
    )
    visible = mapped_column(
        BooleanType, primary_key=True, server_default=boolean_type_default(True)
    )
    gotreplica = mapped_column(GotReplicaType, server_default=GotReplicaDefault(False))


class RunStatus(Base):
    __tablename__ = "runstatus"
    runnumber = mapped_column(NumberType, primary_key=True)
    jobid = mapped_column(NumberType, ForeignKey("jobs.jobid"), primary_key=True)
    finished = mapped_column(BooleanType, server_default=boolean_type_default(False))


class RuntimeProject(Base):
    __tablename__ = "runtimeprojects"
    stepid = mapped_column(NumberType, ForeignKey("steps.stepid"), primary_key=True)
    runtimeprojectid = mapped_column(
        NumberType, ForeignKey("steps.stepid"), primary_key=True
    )


class ProdRunView(Base):
    __tablename__ = "prodrunview"
    production = mapped_column(NumberType, primary_key=True, nullable=False)
    runnumber = mapped_column(NumberType, primary_key=True, nullable=False)
    __table_args__ = (
        UniqueConstraint("production", "runnumber", name="prod_run_const"),
    )


def handle_temp_table_listener(table, dialect, **_):
    if dialect == "sqlite":
        if "TEMPORARY" not in table._prefixes:
            table._prefixes.append("TEMPORARY")
    elif dialect == "mysql":
        if "TEMPORARY" not in table._prefixes:
            table._prefixes.append("TEMPORARY")
    elif dialect == "oracle":
        # For Oracle, we need to use GLOBAL TEMPORARY instead of just TEMPORARY
        if "GLOBAL TEMPORARY" not in table._prefixes:
            table._prefixes.append("GLOBAL TEMPORARY")
    # Note: SQLite and MySQL TEMPORARY tables are automatically dropped when the session ends
    # Oracle GLOBAL TEMPORARY tables with ON COMMIT DELETE ROWS automatically clear after each transaction
    # For explicit clearing in application code, use DELETE or TRUNCATE statements as needed


class TempQueryProductionIds(Base):
    __tablename__ = "temp_query_production_ids"
    __table_args__ = {
        "mysql_engine": "MEMORY",
        "oracle_on_commit": "DELETE ROWS",
    }

    productionid = mapped_column(
        NumberType, primary_key=True, nullable=False, autoincrement=False
    )


class TempQueryFileTypeName(Base):
    __tablename__ = "temp_query_file_type_name"
    __table_args__ = {
        "mysql_engine": "MEMORY",
        "oracle_on_commit": "DELETE ROWS",
    }

    name = mapped_column(
        StringType(64), primary_key=True, nullable=False, autoincrement=False
    )


# Make the table temporary for supported backends
@event.listens_for(TempQueryProductionIds.__table__, "before_create")
def _make_temp_query_production_ids_temp(table, connection, **_):
    handle_temp_table_listener(table, connection.dialect.name)


@event.listens_for(TempQueryFileTypeName.__table__, "before_create")
def _make_temp_query_file_type_name_temp(table, connection, **_):
    handle_temp_table_listener(table, connection.dialect.name)


TEMPORARY_TABLES = [
    TempQueryProductionIds.__table__,
    TempQueryFileTypeName.__table__,
]


async def clear_temp_tables(connection):
    """Clear known temporary tables for MySQL and SQLite. Call manually if needed."""
    if connection.engine.dialect.name not in ("mysql", "sqlite"):
        return

    for table in TEMPORARY_TABLES:
        await connection.execute(table.delete())
