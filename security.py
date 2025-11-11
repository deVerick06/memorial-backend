from passlib.context import CryptContext
import argon2
from datetime import datetime, timedelta
from jose import jwt
from config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

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