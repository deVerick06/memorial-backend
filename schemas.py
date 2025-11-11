from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class HomenagemBase(BaseModel):
    nome: str
    mensagem: str
    imagem_url: Optional[str] = None

class HomenagemCreate(HomenagemBase):
    pass 

class Homenagem(HomenagemBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class MemoriaBase(BaseModel):
    title: str
    description: Optional[str] = None

class MemoriaCreate(MemoriaBase):
    pass

class Memoria(MemoriaBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class Usuario(UsuarioBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str