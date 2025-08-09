from typing import Callable, Dict
from uuid import UUID
from maleo_soma.schemas.resource import Resource, ResourceIdentifier
from maleo_cds.enums.coding.procedure import IdentifierType
from maleo_cds.types.base.coding.procedure import IdentifierValueType

IDENTIFIER_TYPE_VALUE_TYPE_MAP: Dict[
    IdentifierType, Callable[..., IdentifierValueType]
] = {
    IdentifierType.ID: int,
    IdentifierType.UUID: UUID,
}

RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="procedures",
            name="Procedures",
            url_slug="procedures",
        )
    ],
    details=None,
)
