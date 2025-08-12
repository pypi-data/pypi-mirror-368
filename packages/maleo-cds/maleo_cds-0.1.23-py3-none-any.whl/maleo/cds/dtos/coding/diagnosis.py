from pydantic import BaseModel, Field
from typing import List, Optional
from maleo.soma.mixins.general import Code, Description, OptionalOrganizationId, UserId
from maleo.soma.mixins.timestamp import Duration
from maleo.cds.mixins.general import OptionalReasoning
from maleo.cds.dtos.coding.record import (
    PersonalRecordDTO,
    SubjectiveRecordDTO,
    ObjectiveRecordDTO,
)


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


class DiagnosisRecordDTO(
    Duration,
    ListOfDiagnosesMixin,
    ObjectiveRecordDTO,
    SubjectiveRecordDTO,
    PersonalRecordDTO,
    UserId,
    OptionalOrganizationId,
):
    pass
