from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from config import settings
from database import engine, Base
import models, schemas, database
from sqlalchemy.orm import Session
import security

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

@app.post("/signup", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_user(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.UsuarioModel).filter(models.UsuarioModel.email == usuario.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email ja esta cadastrado."
        )
    hashed_pass = security.hash_password(usuario.password)

    new_user = models.UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        hashed_password=hashed_pass
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
