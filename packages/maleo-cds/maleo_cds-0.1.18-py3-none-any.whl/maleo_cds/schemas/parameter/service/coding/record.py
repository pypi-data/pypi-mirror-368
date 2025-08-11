from maleo_soma.mixins.parameter import (
    OptionalListOfIds,
    OptionalListOfUuids,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
)
from maleo_soma.schemas.parameter.service import (
    ReadPaginatedMultipleParameterSchema,
    ReadPaginatedMultipleQueryParameterSchema,
)


class ReadMultipleQueryParameter(
    ReadPaginatedMultipleQueryParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameterSchema,
    OptionalListOfUserIds,
    OptionalListOfOrganizationIds,
    OptionalListOfUuids,
    OptionalListOfIds,
):
    pass
