from fastapi import FastAPI, Depends, HTTPException
from config import settings
from database import engine, Base
import models, schemas, database
from sqlalchemy.orm import Session

app = FastAPI()

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
