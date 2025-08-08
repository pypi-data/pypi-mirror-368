from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.mixins.general import Reasoning
from maleo_soma.mixins.general import UserId, OptionalOrganizationId, Code, Description


class DiagnosisDataSchema(
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
