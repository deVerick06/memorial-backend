from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class HomenagemModel(Base):
    __tablename__ = "homenagens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    mensagem = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(512), nullable=True)

class MemoriaModel(Base):
    __tablename__ = "memorias"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(512), nullable=True)

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())