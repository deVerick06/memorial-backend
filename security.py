from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha pura corresponde ao hash salvo."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Gera um hash a partir de uma senha pura."""
    return pwd_context.hash(password)