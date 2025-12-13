# backend/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

# ==============================
# Password hashing (bcrypt)
# ==============================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_PASSWORD_LENGTH = 72  # batas bcrypt

def _truncate_password(password: str) -> str:
    password = str(password)
    return password[:MAX_PASSWORD_LENGTH]

def get_password_hash(password: str) -> str:
    password = _truncate_password(password)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _truncate_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

# ==============================
# JWT config
# ==============================
# NOTE: nanti pindahkan ke .env (lebih aman). Untuk belajar dulu oke.
SECRET_KEY = "ganti_ini_dengan_string_random_panjang_banget"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    """
    data biasanya berisi:
    - sub: user_id (string)
    - role: role user
    """
    to_encode = data.copy()
    minutes = expires_minutes if expires_minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Return payload dict kalau token valid.
    Raise JWTError kalau token invalid/expired.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
