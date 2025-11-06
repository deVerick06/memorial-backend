from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class HomenagemModel(Base):
    __tablename__ = "homenagens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    mensagem = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())