from sqlalchemy import Column, Integer, Text
from maleo_soma.models.table import DataTable
from maleo_cds.db import MaleoCDSBase


class CodingDiagnosesMixin:
    organization_id = Column(name="organization_id", type_=Integer)
    user_id = Column(name="user_id", type_=Integer, nullable=False)
    code = Column(name="code", type_=Text, nullable=False)
    description = Column(name="description", type_=Text, nullable=False)
    reasoning = Column(name="reasoning", type_=Text, nullable=False)


class CodingDiagnosesTable(CodingDiagnosesMixin, DataTable, MaleoCDSBase):
    __tablename__ = "coding_diagnoses"
