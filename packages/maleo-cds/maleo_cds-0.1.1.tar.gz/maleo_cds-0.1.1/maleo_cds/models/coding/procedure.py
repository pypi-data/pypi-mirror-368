from sqlalchemy import Column, Integer, String, Text
from maleo_soma.models.table import DataTable
from maleo_cds.db import MaleoCDSBase


class ProceduresMixin:
    organization_id = Column(name="organization_id", type_=Integer)
    user_id = Column(name="user_id", type_=Integer, nullable=False)
    code = Column(name="code", type_=String(20), unique=True, nullable=False)
    description = Column(name="description", type_=Text)
    reasoning = Column(name="reasoning", type_=Text)


class ProceduresTable(ProceduresMixin, DataTable, MaleoCDSBase):
    __tablename__ = "procedures"
