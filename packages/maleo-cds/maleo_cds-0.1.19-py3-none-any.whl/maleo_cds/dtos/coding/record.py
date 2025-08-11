from maleo_soma.mixins.general import OptionalAge
from maleo_metadata.schemas.data.gender import OptionalSimpleGenderMixin
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


class PersonalRecordDTO(
    OptionalAge,
    OptionalSimpleGenderMixin,
):
    pass


class SubjectiveRecordDTO(
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
):
    pass


class ObjectiveRecordDTO(
    OptionalOrganExaminationDetail,
    OptionalBodyMassIndex,
    OptionalWeight,
    OptionalHeight,
    OptionalWaistCircumference,
    OptionalAbdominalCircumference,
    OptionalOxygenSaturation,
    OptionalHeartRate,
    OptionalRespirationRate,
    OptionalTemperature,
    OptionalDiastolicBloodPressure,
    OptionalSystolicBloodPressure,
):
    pass


class PlanRecordDTO(OptionalTreatment, OptionalOverallPlan):
    pass
