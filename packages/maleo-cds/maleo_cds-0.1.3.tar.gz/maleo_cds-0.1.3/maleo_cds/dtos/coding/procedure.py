from maleo_cds.mixins.general import Reasoning
from maleo_soma.mixins.general import Code, Description


class ProcedureDataDTO(
    Reasoning,
    Description,
    Code[str],
):
    pass
