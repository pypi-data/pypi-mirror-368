from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.dtos.coding.procedure import ProcedureDataDTO
from maleo_soma.mixins.general import UserId, OptionalOrganizationId


class ProcedureDataSchema(
    ProcedureDataDTO,
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
