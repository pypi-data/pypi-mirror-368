from maleo_soma.mixins.general import OptionalOrganizationId, UserId
from maleo_soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo_soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo_cds.dtos.coding.diagnosis import ListOfDiagnosesMixin
from maleo_cds.dtos.coding.procedure import CompleteProcedureMixin
from maleo_cds.dtos.coding.record import (
    PersonalRecordDTO,
    SubjectiveRecordDTO,
    ObjectiveRecordDTO,
    PlanRecordDTO,
)
from maleo_cds.enums.coding.record import IdentifierType
from maleo_cds.types.base.coding.record import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class CreateOrUpdateBody(
    CompleteProcedureMixin,
    PlanRecordDTO,
    ListOfDiagnosesMixin,
    ObjectiveRecordDTO,
    SubjectiveRecordDTO,
    PersonalRecordDTO,
):
    pass


class CreateParameter(CreateOrUpdateBody, UserId, OptionalOrganizationId):
    pass


class UpdateParameter(
    CreateOrUpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass
