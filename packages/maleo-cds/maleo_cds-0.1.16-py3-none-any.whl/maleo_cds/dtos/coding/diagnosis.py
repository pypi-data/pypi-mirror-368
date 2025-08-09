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


class DiagnosisMixin(BaseModel):
    diagnosis: DiagnosisDataDTO = Field(..., description="Single diagnosis data")


class OptionalDiagnosisMixin(BaseModel):
    diagnosis: Optional[DiagnosisDataDTO] = Field(
        None, description="Single diagnosis data. (Optional)"
    )


class ListOfDiagnosesMixin(BaseModel):
    diagnoses: List[DiagnosisDataDTO] = Field(
        ..., description="Multiple diagnoses data"
    )


class OptionalListOfDiagnosesMixin(BaseModel):
    diagnoses: Optional[List[DiagnosisDataDTO]] = Field(
        None, description="Multiple diagnoses data. (Optional)"
    )
