from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_soma.mixins.general import UserId, OptionalOrganizationId, OptionalAge
from maleo_metadata.schemas.data.gender import OptionalSimpleGender
from maleo_cds.mixins.general import (
    ChiefComplaint,
    OptionalAdditionalComplaint,
    OptionalPainScale,
    OptionalOnset,
    OptionalChronology,
    OptionalLocation,
    OptionalAggravatingFactor,
    OptionalRelievingFactor,
    OptionalPersonalMedicalHistory,
    OptionalFamilyMedicalHistory,
    OptionalHabitActivityOccupation,
    OptionalConsumedMedication,
    OptionalSystolicBloodPressure,
    OptionalDiastolicBloodPressure,
    OptionalTemperature,
    OptionalRespirationRate,
    OptionalHeartRate,
    OptionalOxygenSaturation,
    OptionalAbdominalCircumference,
    OptionalWaistCircumference,
    OptionalWeight,
    OptionalHeight,
    OptionalBodyMassIndex,
    OptionalOrganExaminationDetail,
    OptionalOverallPlan,
    OptionalTreatment,
)
from .diagnosis import ListOfDiagnosesMixin
from .procedure import ProcedureRecommendationSchemaMixin


class RecordDataSchema(
    ProcedureRecommendationSchemaMixin,
    OptionalTreatment,
    OptionalOverallPlan,
    ListOfDiagnosesMixin,
    OptionalOrganExaminationDetail,
    OptionalBodyMassIndex,
    OptionalHeight,
    OptionalWeight,
    OptionalWaistCircumference,
    OptionalAbdominalCircumference,
    OptionalOxygenSaturation,
    OptionalHeartRate,
    OptionalRespirationRate,
    OptionalTemperature,
    OptionalDiastolicBloodPressure,
    OptionalSystolicBloodPressure,
    OptionalConsumedMedication,
    OptionalHabitActivityOccupation,
    OptionalFamilyMedicalHistory,
    OptionalPersonalMedicalHistory,
    OptionalRelievingFactor,
    OptionalAggravatingFactor,
    OptionalLocation,
    OptionalChronology,
    OptionalOnset,
    OptionalPainScale,
    OptionalAdditionalComplaint,
    ChiefComplaint,
    OptionalAge,
    OptionalSimpleGender,
    UserId,
    OptionalOrganizationId,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass


class ExpandedRecord(BaseModel):
    record: RecordDataSchema = Field(..., description="Single record data")


class OptionalExpandedRecord(BaseModel):
    record: Optional[RecordDataSchema] = Field(
        None, description="Single record data. (Optional)"
    )


class ListOfExpandedRecords(BaseModel):
    records: List[RecordDataSchema] = Field(..., description="Multiple records data")


class OptionalListOfExpandedRecords(BaseModel):
    records: Optional[List[RecordDataSchema]] = Field(
        None, description="Multiple records data. (Optional)"
    )
