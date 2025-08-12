from sqlalchemy import Column, Integer, Text, JSON
from maleo_soma.models.table import DataTable
from maleo_cds.db import MaleoCDSBase


class CodingProceduresMixin:
    organization_id = Column(name="organization_id", type_=Integer)
    user_id = Column(name="user_id", type_=Integer, nullable=False)
    overall_plan = Column(name="overall_plan", type_=Text)
    treatment = Column(name="treatment", type_=Text)
    procedure = Column(name="procedure", type_=JSON)


class CodingProceduresTable(CodingProceduresMixin, DataTable, MaleoCDSBase):
    __tablename__ = "coding_procedures"
