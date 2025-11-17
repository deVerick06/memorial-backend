from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class VelaBase(BaseModel):
    pass 

class Vela(VelaBase):
    id: int
    user_id: int
    homenagem_id: int

    class Config:
        from_attributes = True

class ComentarioBase(BaseModel):
    texto: str

class ComentarioCreate(ComentarioBase):
    pass

class Comentario(ComentarioBase):
    id: int
    user_id: int
    homenagem_id: int
    criado_em: datetime
    nome_usuario: str

    class Config:
        from_attributes = True

class HomenagemBase(BaseModel):
    nome: str
    mensagem: str
    image_url: Optional[str] = None

class HomenagemCreate(HomenagemBase):
    pass 

class Homenagem(HomenagemBase):
    id: int
    criado_em: datetime
    owner_id: int
    total_velas: int = 0
    velas_acesas_por_mim: bool = False
    comentarios: list[Comentario] = []

    class Config:
        from_attributes = True

class MemoriaBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class MemoriaCreate(MemoriaBase):
    pass

class Memoria(MemoriaBase):
    id: int
    criado_em: datetime
    owner_id: int

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