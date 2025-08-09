from maleo_cds.mixins.general import OptionalReasoning
from maleo_soma.mixins.general import Code, Description


class ProcedureDataDTO(
    OptionalReasoning,
    Description,
    Code[str],
):
    pass
