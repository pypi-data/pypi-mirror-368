from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.dtos.coding.procedure import ProcedureDataDTO


class ProcedureRecordSchema(
    ProcedureDataDTO,
    DataTimestamp,
    DataStatus,
    DataIdentifier,
):
    pass
