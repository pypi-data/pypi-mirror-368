from maleo_soma.mixins.general import OptionalAge
from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.schemas.data.gender import OptionalSimpleGender
from maleo_cds.enums.coding.record import IdentifierType
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
from maleo_cds.schemas.data.coding.diagnosis import ListOfDiagnosesMixin
from maleo_cds.schemas.data.coding.procedure import ProcedureRecommendationSchemaMixin
from maleo_cds.types.base.coding.record import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateOrUpdateParameter(
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
):
    pass
