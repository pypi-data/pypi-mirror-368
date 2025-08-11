from pydantic import BaseModel, Field
from typing import List
from maleo_cds.mixins.general import OptionalReasoning
from maleo_soma.mixins.general import Code, Description


class ProcedureDataDTO(
    OptionalReasoning,
    Description,
    Code[str],
):
    pass


class CompleteProcedureDTO(BaseModel):
    primary: List[ProcedureDataDTO] = Field(..., description="Primary procedures")
    alternatives: List[ProcedureDataDTO] = Field(
        ..., description="Alternative procedures"
    )


class CompleteProcedureMixin(BaseModel):
    procedure: CompleteProcedureDTO = Field(..., description="Complete procedure")
