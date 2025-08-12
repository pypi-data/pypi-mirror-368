from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.dtos.coding.procedure import ProcedureRecordDTO


class ProcedureRecordSchema(
    ProcedureRecordDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass
