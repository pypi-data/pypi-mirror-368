from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_cds.enums.coding.procedure import IdentifierType
from maleo_cds.mixins.general import OptionalOverallPlan, OptionalTreatment
from maleo_cds.types.base.coding.procedure import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class GenerateRecommendationParameter(
    OptionalTreatment,
    OptionalOverallPlan,
):
    @property
    def prompt_format(self) -> str:
        sections = []
        if self.overall_plan is not None:
            sections.append(f"Plan Umum: {self.overall_plan}")
        if self.treatment is not None:
            sections.append(f"Tindakan: {self.treatment}")

        return "\n".join(sections)
