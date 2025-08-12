from maleo_soma.mixins.data import DataIdentifier, DataStatus, DataTimestamp
from maleo_cds.dtos.coding.diagnosis import DiagnosisRecordDTO


class DiagnosisRecordSchema(
    DiagnosisRecordDTO,
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    pass
