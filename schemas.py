from pydantic import BaseModel
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