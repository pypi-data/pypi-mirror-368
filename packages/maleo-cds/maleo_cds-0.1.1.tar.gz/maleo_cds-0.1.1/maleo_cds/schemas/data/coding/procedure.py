from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.mixins.general import Reasoning
from maleo_soma.mixins.general import UserId, OptionalOrganizationId, Code, Description


class ProcedureDataSchema(
    Reasoning,
    Description,
    Code[str],
    UserId,
    OptionalOrganizationId,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class ExpandedProcedure(BaseModel):
    procedure: ProcedureDataSchema = Field(..., description="Single procedure data")


class OptionalExpandedProcedure(BaseModel):
    procedure: Optional[ProcedureDataSchema] = Field(
        None, description="Single procedure data. (Optional)"
    )


class ListOfExpandedProcedures(BaseModel):
    procedures: List[ProcedureDataSchema] = Field(
        ..., description="Multiple procedures data"
    )


class OptionalListOfExpandedProcedures(BaseModel):
    procedures: Optional[List[ProcedureDataSchema]] = Field(
        None, description="Multiple procedures data. (Optional)"
    )
