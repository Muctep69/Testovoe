from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from app import crud

# Секретный ключ для подписи и верификации JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Создание объекта для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 PasswordBearer для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функция для генерации JWT токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    # Устанавливаем срок действия токена
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для декодирования и верификации JWT токена
def decode_token(token: str):
    try:
        # Декодируем токен и проверяем его подпись
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # Возвращаем None в случае ошибки
        print(f"JWT decoding error: {e}")
        return None

# Функция для аутентификации пользователя
def authenticate_user(username: str, plain_password: str, db: Session):
    # Получаем пользователя из базы данных по его имени пользователя
    user = crud.get_user_by_username(db, username)
    # Проверяем, существует ли пользователь и совпадает ли введенный пароль с хэшированным паролем пользователя
    if not user:

        return None
    if not verify_password(plain_password, user.password):

        return None
    return user

def verify_password(plain_password, hashed_password):
    result = pwd_context.verify(plain_password, hashed_password)

    return result

# Функция для хэширования пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для получения текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = crud.get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
