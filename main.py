from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from config import settings
from database import engine, Base
import models, schemas, database
from sqlalchemy.orm import Session

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.post("/homenagens/", response_model=schemas.Homenagem)
def create_homenagem(homenagem: schemas.HomenagemCreate, db: Session = Depends(database.get_db)):
    nova_homenagem = models.HomenagemModel(
        nome=homenagem.nome,
        mensagem=homenagem.mensagem
    )
    db.add(nova_homenagem)
    db.commit()
    db.refresh(nova_homenagem)
    return nova_homenagem

@app.get("/homenagens/", response_model=list[schemas.Homenagem])
def read_homenagens(db: Session = Depends(database.get_db)):
    homenagens = db.query(models.HomenagemModel).all()
    return homenagens

@app.post("/memorias/", response_model=schemas.Memoria)
def create_memoria(memoria: schemas.MemoriaCreate, db: Session = Depends(database.get_db)):
    new_memory = models.MemoriaModel(
        title=memoria.title,
        description=memoria.description
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory

@app.get("/memorias/", response_model=list[schemas.Memoria])
def read_memorias(db: Session = Depends(database.get_db)):
    memorys = db.query(models.MemoriaModel).all()
    return memorys
