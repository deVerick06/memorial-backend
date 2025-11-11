from passlib.context import CryptContext
import argon2
from datetime import datetime, timedelta
from jose import jwt
from config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import database, models, schemas

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha pura corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Gera um hash a partir de uma senha pura."""
    return pwd_context.hash(password)

def create_access_token(subject: str) -> str:
    """
    Cria um nova Token do Acesso (nosso "cracha") para um usuario.
    O 'subject' (assunto) do token sera o email do usuario.
    """

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": subject,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
) -> models.UsuarioModel:
    """
    Pega o token do header.
    Decodifica o token.
    Pega o email (o 'sub') de dentro dele.
    Busca o usuario no banco de dados com esse email.
    Retorna o objeto do usuario ou um erro.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    
    except jwt.JWTError :
        raise credentials_exception
    
    user = db.query(models.UsuarioModel).filter(models.UsuarioModel.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user