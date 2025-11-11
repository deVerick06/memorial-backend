from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from config import settings
from database import engine, Base
import models, schemas, database
from sqlalchemy.orm import Session
import security
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import UploadFile, File
import storage_client
import uuid

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
def create_homenagem(
    homenagem: schemas.HomenagemCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    nova_homenagem = models.HomenagemModel(
        nome=homenagem.nome,
        mensagem=homenagem.mensagem
    )
    db.add(nova_homenagem)
    db.commit()
    db.refresh(nova_homenagem)
    return nova_homenagem

@app.get("/homenagens/", response_model=list[schemas.Homenagem])
def read_homenagens(
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    homenagens = db.query(models.HomenagemModel).all()
    return homenagens

@app.post("/memorias/", response_model=schemas.Memoria)
def create_memoria(
    memoria: schemas.MemoriaCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    new_memory = models.MemoriaModel(
        title=memoria.title,
        description=memoria.description
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory

@app.get("/memorias/", response_model=list[schemas.Memoria])
def read_memorias(
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
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

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    usuario = db.query(models.UsuarioModel).filter(
        models.UsuarioModel.email == form_data.username
    ).first()

    if not usuario or not security.verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        subject=usuario.email
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload-image/")
def upload_image(
    file: UploadFile = File(...),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    """
    Recebe um arquivo de imagem, Salva no Storage e retorna a URL publica.
    """
    try:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        bucket_path = f"imagem/{file_name}"

        storage_client.storage_client.from_("imagem").upload(
            path=file_name,
            file=file.file.read(),
            file_options={"content-type": file.content_type}
        )

        public_url = storage_client.storage_client.from_("imagem").get_public_url(file_name)

        return {"image_url": public_url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload da imagem: {str(e)}"
        )