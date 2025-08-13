from enum import Enum
from typing import List, Optional

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, model_validator


class BaseModel(_BaseModel):
    """Base model class with a suitable model_config default."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class BooleanYN(str, Enum):
    """Boolean values represented as Y/N strings."""

    YES = "Y"
    NO = "N"


class UsableStatus(str, Enum):
    """Possible values for the usable field in Steps."""

    YES = "Yes"
    NOT_READY = "Not ready"
    OBSOLETE = "Obsolete"


class GotReplicaStatus(str, Enum):
    """Possible values for gotreplica field."""

    YES = "Yes"
    NO = "No"


class FileTypeModel(BaseModel):
    """Model for file types in input/output file types array."""

    name: str
    visible: BooleanYN = BooleanYN.YES


# Configuration Models


class ConfigurationInsert(BaseModel):
    """Model for inserting configurations."""

    configurationid: Optional[int] = None
    configname: str
    configversion: str


# SimulationCondition Models


class SimulationConditionInsert(BaseModel):
    """Model for inserting simulation conditions."""

    simid: Optional[int] = None
    simdescription: str
    beamcond: str
    beamenergy: str
    generator: str
    magneticfield: str
    detectorcond: str
    luminosity: str
    g4settings: Optional[str] = ""
    visible: BooleanYN = BooleanYN.YES


# DataTakingCondition Models


class DataTakingConditionInsert(BaseModel):
    """Model for inserting data taking conditions."""

    daqperiodid: Optional[int] = None
    description: str
    beamcond: str
    beamenergy: str
    magneticfield: str
    velo: str
    it: str
    tt: str
    ot: str
    rich1: str
    rich2: str
    spd_prs: str
    ecal: str
    hcal: str
    muon: str
    l0: str
    hlt: str
    veloposition: str


# EventType Models

EventTypeInsert = int


# ProductionsContainer Models


class ProductionContainerInsert(BaseModel):
    """Model for inserting production containers."""

    production: Optional[int] = None
    processingid: int
    simid: Optional[int] = None
    daqperiodid: Optional[int] = None
    totalprocessing: str
    configurationid: int

    @model_validator(mode="after")
    def validate_simulation_or_data_taking(self) -> "ProductionContainerInsert":
        """Validate that either simid or daqperiodid is provided."""
        if self.simid is None and self.daqperiodid is None:
            raise ValueError("Either simid or daqperiodid must be provided")
        return self


# Job Models


class JobInsert(BaseModel):
    """Model for inserting jobs."""

    jobid: Optional[int] = None
    name: str
    configurationid: int
    diracjobid: int
    production: int
    stepid: int

    # Optional fields
    diracversion: Optional[str] = None
    eventinputstat: Optional[int] = None
    exectime: Optional[float] = None
    firsteventnumber: Optional[int] = None
    geometryversion: Optional[str] = None
    gridjobid: Optional[str] = None
    jobend: Optional[str] = None
    jobstart: Optional[str] = None
    localjobid: Optional[str] = None
    LOCATION: Optional[str] = None
    numberofevents: Optional[int] = None
    programname: Optional[str] = None
    programversion: Optional[str] = None
    statisticsrequested: Optional[int] = None
    wncpupower: Optional[str] = None
    cputime: Optional[float] = None
    wncache: Optional[str] = None
    wnmemory: Optional[str] = None
    wnmodel: Optional[str] = None
    workernode: Optional[str] = None
    generator: Optional[str] = None
    runnumber: Optional[int] = None
    fillnumber: Optional[int] = None
    wncpuhs06: Optional[float] = 0.0
    totalluminosity: Optional[int] = 0
    tck: Optional[str] = "None"
    wnmjfhs06: Optional[float] = None
    hlt2tck: Optional[str] = None
    numberofprocessors: Optional[int] = 1


# File Models


class FileInsert(BaseModel):
    """Model for inserting files."""

    fileid: Optional[int] = None
    filename: str
    guid: str
    md5sum: str
    eventtypeid: int
    filetypeid: int
    jobid: int
    production: int
    visibilityflag: BooleanYN = BooleanYN.YES

    # Optional fields
    adler32: Optional[str] = None
    creationdate: Optional[str] = None
    eventstat: Optional[int] = None
    gotreplica: GotReplicaStatus = GotReplicaStatus.NO
    filesize: Optional[int] = 0
    qualityid: Optional[int] = 1
    fullstat: Optional[int] = None
    physicstat: Optional[int] = None
    luminosity: Optional[int] = 0
    instluminosity: Optional[int] = 0

    @model_validator(mode="after")
    def validate_physicstat(self) -> "FileInsert":
        """Validate that physicstat is negative if provided."""
        if self.physicstat is not None and self.physicstat >= 0:
            raise ValueError("physicstat must be negative")
        return self


# StepsContainer Models


class StepsContainerInsert(BaseModel):
    """Model for inserting steps containers."""

    production: int
    stepid: int
    step: Optional[int] = 1
    eventtypeid: Optional[int] = None


# ProductionOutputFile Models


class ProductionOutputFileInsert(BaseModel):
    """Model for inserting production output files."""

    production: int
    stepid: int
    eventtypeid: int
    filetypeid: int
    visible: BooleanYN = BooleanYN.YES
    gotreplica: GotReplicaStatus = GotReplicaStatus.NO


# Step Models


class StepInsert(BaseModel):
    """Model for inserting steps."""

    stepid: Optional[int] = None
    stepname: str
    applicationname: str
    applicationversion: str
    processingpass: str
    visible: BooleanYN = BooleanYN.YES
    inputfiletypes: List[FileTypeModel]
    outputfiletypes: List[FileTypeModel]
    ismulticore: BooleanYN = BooleanYN.NO

    # Optional fields
    optionfiles: Optional[str] = None
    dddb: Optional[str] = None
    conddb: Optional[str] = None
    extrapackages: Optional[str] = None
    usable: UsableStatus = UsableStatus.NOT_READY
    dqtag: Optional[str] = None
    optionsformat: Optional[str] = None
    systemconfig: Optional[str] = None
    mctck: Optional[str] = None


# FileType Models


class FileTypeInsert(BaseModel):
    """Model for inserting file types."""

    filetypeid: Optional[int] = None
    name: str
    version: str = "1"
    description: str = ""


# Processing Models


class ProcessingInsert(BaseModel):
    """Model for inserting processing passes."""

    id: Optional[int] = None
    parentid: int
    name: str
