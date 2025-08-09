from pydantic import BaseModel, Field
from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_soma.types.base import OptionalString
from maleo_cds.enums.coding.procedure import IdentifierType
from maleo_cds.types.base.coding.procedure import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class GenerateRecommendationParameter(BaseModel):
    overall_plan: str = Field(..., description="Overall plan")
    treatment: OptionalString = Field(None, description="Treatment. (Optional)")
