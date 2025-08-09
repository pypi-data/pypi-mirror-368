from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.dtos.coding.diagnosis import DiagnosisDataDTO
from maleo_soma.mixins.general import UserId, OptionalOrganizationId


class DiagnosisDataSchema(
    DiagnosisDataDTO,
    UserId,
    OptionalOrganizationId,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class ExpandedDiagnosis(BaseModel):
    diagnosis: DiagnosisDataSchema = Field(..., description="Single diagnosis data")


class OptionalExpandedDiagnosis(BaseModel):
    diagnosis: Optional[DiagnosisDataSchema] = Field(
        None, description="Single diagnosis data. (Optional)"
    )


class ListOfExpandedDiagnoses(BaseModel):
    diagnoses: List[DiagnosisDataSchema] = Field(
        ..., description="Multiple diagnoses data"
    )


class OptionalListOfExpandedDiagnoses(BaseModel):
    diagnoses: Optional[List[DiagnosisDataSchema]] = Field(
        None, description="Multiple diagnoses data. (Optional)"
    )
