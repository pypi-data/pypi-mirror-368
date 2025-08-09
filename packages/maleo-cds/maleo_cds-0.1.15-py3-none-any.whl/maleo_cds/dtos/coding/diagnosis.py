from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_cds.mixins.general import OptionalReasoning
from maleo_soma.mixins.general import Code, Description


class DiagnosisDataDTO(
    OptionalReasoning,
    Description,
    Code[str],
):
    pass


class DiagnosisDataMixin(BaseModel):
    diagnosis: DiagnosisDataDTO = Field(..., description="Single diagnosis data")


class OptionalDiagnosisDataMixin(BaseModel):
    diagnosis: Optional[DiagnosisDataDTO] = Field(
        None, description="Single diagnosis data. (Optional)"
    )


class ListOfDiagnosesDataMixin(BaseModel):
    diagnoses: List[DiagnosisDataDTO] = Field(
        ..., description="Multiple diagnoses data"
    )


class OptionalListOfDiagnosesDataMixin(BaseModel):
    diagnoses: Optional[List[DiagnosisDataDTO]] = Field(
        None, description="Multiple diagnoses data. (Optional)"
    )
