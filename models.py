from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    profile_pic_url = Column(String(512), nullable=True)
    memorias = relationship("MemoriaModel", back_populates="owner")
    homenagens = relationship("HomenagemModel", back_populates="owner")

class MemoriaModel(Base):
    __tablename__ = "memorias"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(512), nullable=True)
    owner_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    owner = relationship("UsuarioModel", back_populates="memorias")

class HomenagemModel(Base):
    __tablename__ = "homenagens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    mensagem = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(512), nullable=True)
    velas = relationship("VelaModel", back_populates="homenagem", cascade="all, delete-orphan")
    comentarios = relationship("ComentarioModel", back_populates="homenagem", cascade="all, delete-orphan")
    owner_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    owner = relationship("UsuarioModel", back_populates="homenagens")


class VelaModel(Base):
    __tablename__ = "velas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    homenagem_id = Column(Integer, ForeignKey("homenagens.id"), nullable=False)
    user = relationship("UsuarioModel")
    homenagem = relationship("HomenagemModel", back_populates="velas")

class ComentarioModel(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    homenagem_id = Column(Integer, ForeignKey("homenagens.id"), nullable=False)
    user = relationship("UsuarioModel")
    homenagem = relationship("HomenagemModel", back_populates="comentarios")