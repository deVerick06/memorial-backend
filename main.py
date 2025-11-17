from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status
from config import settings
from database import engine, Base
import models, schemas, database
from sqlalchemy.orm import Session
import security
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import UploadFile, File
from storage_client import supabase_client
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
        mensagem=homenagem.mensagem,
        image_url=homenagem.image_url,
        owner_id = current_user.id
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
    homenagens_db = db.query(models.HomenagemModel).all()

    resultado = []
    for h in homenagens_db:
        lit = any(v.user_id == current_user.id for v in h.velas)
        formatted_comments = []
        for c in h.comentarios:
            comment_owner = db.query(models.UsuarioModel).filter(models.UsuarioModel.id == c.user_id).first()
            nome = comment_owner.nome if comment_owner else "Desconhecido"

            formatted_comments.append({
                "id": c.id,
                "texto": c.texto,
                "user_id": c.user_id,
                "homenagem_id": c.homenagem_id,
                "criado_em": c.criado_em,
                "nome_usuario": nome
            })
        h_schema = {
            "id": h.id,
            "nome": h.nome,
            "mensagem": h.mensagem,
            "image_url": h.image_url,
            "owner_id": h.owner_id,
            "criado_em": h.criado_em,
            "total_velas": len(h.velas),
            "velas_acesas_por_mim": lit,
            "comentarios": formatted_comments
        }
        resultado.append(h_schema)
    return resultado

@app.post("/memorias/", response_model=schemas.Memoria)
def create_memoria(
    memoria: schemas.MemoriaCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    new_memory = models.MemoriaModel(
        title=memoria.title,
        description=memoria.description,
        image_url=memoria.image_url,
        owner_id = current_user.id
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
    memorys = db.query(models.MemoriaModel).filter(models.MemoriaModel.owner_id == current_user.id).all()
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
    print("--- ROTA /upload-image/ CHAMADA ---") 
    try:

        bucket_name = "imagem" 

        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"

        print(f"Tentando upload para o balde: {bucket_name}, com o nome: {file_name}")

        supabase_client.storage.from_(bucket_name).upload(
            path=file_name,
            file=file.file.read(),
            file_options={"content-type": file.content_type}
        )
        print("--- Upload no Supabase CONCLUÍDO ---")

        public_url = supabase_client.storage.from_(bucket_name).get_public_url(file_name)
        print(f"URL pública gerada: {public_url}")

        return {"image_url": public_url}

    except Exception as e:

        print(f"!!! ERRO NO UPLOAD: {repr(e)}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload: {repr(e)}" 
        )
    
@app.delete("/memorias/{memoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memoria(
    memoria_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    memoria_db = db.query(models.MemoriaModel).filter(models.MemoriaModel.id == memoria_id).first()

    if memoria_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memória não encontrada"
        )
    if memoria_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida"
        )
    
    db.delete(memoria_db)
    db.commit()

    return

@app.put("/memorias/{memoria_id}", response_model=schemas.Memoria)
def update_memoria(
    memoria_id: int,
    memoria_data: schemas.MemoriaCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    memoria_db = db.query(models.MemoriaModel).filter(models.MemoriaModel.id == memoria_id).first()

    if memoria_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memória não encontrada"
        )
    if memoria_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida"
        )
    
    memoria_db.title = memoria_data.title
    memoria_db.description = memoria_data.description

    db.commit()
    db.refresh(memoria_db)

    return memoria_db

@app.get("/users/me", response_model=schemas.Usuario)
def read_users_me(
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    return current_user

@app.delete("/homenagens/{homenagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homenagem(
    homenagem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    homenagem_db = db.query(models.HomenagemModel).filter(models.HomenagemModel.id == homenagem_id).first()
    if homenagem_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homenagem não encontrada"
        )
    
    if homenagem_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida"
        )
    db.delete(homenagem_db)
    db.commit()
    return

@app.put("/homenagens/{homenagem_id}")
def update_homenagem(
    homenagem_id: int,
    homenagem_data: schemas.HomenagemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    homenagem_db = db.query(models.HomenagemModel).filter(models.HomenagemModel.id == homenagem_id).first()
    if homenagem_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homenagem não encontrada"
        )
    
    if homenagem_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação não permitida"
        )
    homenagem_db.nome = homenagem_data.nome
    homenagem_db.mensagem = homenagem_data.mensagem

    db.commit()
    db.refresh(homenagem_db)
    return homenagem_db

@app.post("/homenagens/{homenagem_id}/vela")
def toggle_vela(
    homenagem_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    vela_existing = db.query(models.VelaModel).filter(
        models.VelaModel.user_id == current_user.id,
        models.VelaModel.homenagem_id == homenagem_id
    ).first()

    if vela_existing:
        db.delete(vela_existing)
        db.commit()
        return {"status": "apagada"}
    else:
        new_vela = models.VelaModel(user_id=current_user.id, homenagem_id=homenagem_id)
        db.add(new_vela)
        db.commit()
        return {"status": "acesa"}

@app.post("/homenagens/{homenagem_id}/comentarios", response_model=schemas.Comentario)
def create_comentario(
    homenagem_id: int,
    comentarios: schemas.ComentarioCreate,
    db: Session = Depends(database.get_db),
    current_user: models.UsuarioModel = Depends(security.get_current_user)
):
    new_comentario = models.ComentarioModel(
        texto=comentarios.texto,
        user_id=current_user.id,
        homenagem_id=homenagem_id
    )
    db.add(new_comentario)
    db.commit()
    db.refresh(new_comentario)

    return {
        "id": new_comentario.id,
        "texto": new_comentario.texto,
        "user_id": new_comentario.user_id,
        "homenagem_id": new_comentario.homenagem_id,
        "criado_em": new_comentario.criado_em,
        "nome_usuario": current_user.nome
    }