from pydantic import BaseModel, model_validator
from typing import Self
from maleo_soma.mixins.general import OptionalAge
from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_metadata.schemas.data.gender import OptionalSimpleGender
from maleo_cds.enums.coding.diagnosis import IdentifierType
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
)
from maleo_cds.types.base.coding.diagnosis import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class GenerateDifferentialDiagnosisParameter(
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
    BaseModel,
):

    @model_validator(mode="after")
    def calculate_bmi(self) -> Self:
        if self.weight is not None and self.height is not None and self.height > 0:
            self.body_mass_index = self.weight / (self.height**2)
        return self

    @property
    def prompt_format(self) -> str:
        if (
            self.systolic_blood_pressure is None
            and self.diastolic_blood_pressure is None
        ):
            blood_pressure_str = "Not provided"
        else:
            systolic_blood_pressure_str = f"{self.systolic_blood_pressure if self.systolic_blood_pressure is not None else "Not provided"}"
            diastolic_blood_pressure_str = f"{self.diastolic_blood_pressure if self.diastolic_blood_pressure is not None else "Not provided"}"
            blood_pressure_str = (
                f"{systolic_blood_pressure_str}/{diastolic_blood_pressure_str}"
            )
        return f"""
            Chief complaint: {self.chief_complaint}
            Additional vomplaint: {self.additional_complaint}
            Organ examination detail: {self.organ_examination_detail}

            [Clinical Measurements]
            Blood Pressure (mmHg): {blood_pressure_str}
            Body Temperature (Celcius): {self.temperature if self.temperature is not None else "Not provided"}
            Respiration Rate (Breaths/Minute): {self.respiration_rate if self.respiration_rate is not None else "Not provided"}
            Heart Rate (Beats/Minute): {self.heart_rate if self.heart_rate is not None else "Not provided"}
            SpO2 (%): {self.oxygen_saturation if self.oxygen_saturation is not None else "Not provided"}
            Abodminal Circumference (cm): {self.abdominal_circumference if self.abdominal_circumference is not None else "Not provided"}
            Waist Circumference (cm): {self.waist_circumference if self.waist_circumference is not None else "Not provided"}
            Height (cm): {self.height if self.height is not None else "Not provided"}
            Weight (Kg): {self.weight if self.weight is not None else "Not provided"}
            Body Mass Index (Kg/m2): {f"{self.body_mass_index:.2f}" if self.body_mass_index is not None else "Not provided"}
            """
