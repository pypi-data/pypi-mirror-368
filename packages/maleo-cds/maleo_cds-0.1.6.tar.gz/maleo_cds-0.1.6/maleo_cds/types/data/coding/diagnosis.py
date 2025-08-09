from typing import List, Optional
from maleo_cds.schemas.data.coding.diagnosis import DiagnosisDataSchema


# Exapanded diagnoses
ExpandedDiagnoses = DiagnosisDataSchema
OptionalExpandedDiagnoses = Optional[ExpandedDiagnoses]
ListOfExpandedDiagnoses = List[ExpandedDiagnoses]
OptionalListOfExpandedDiagnoses = Optional[List[ExpandedDiagnoses]]
