# Handles token creation and verification for users

from jose import jwt, JWTError
from datetime import datetime, timedelta
from . import classes, dbConnection
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

secret_key = settings.secret_key
algorithm = settings.algorithm
access_token_expiration_minutes = settings.access_token_expires_in

cursor = dbConnection.cursor

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=access_token_expiration_minutes)

    to_encode.update({"exp": expire})

    final_encode = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return final_encode

def verify_token(token: str, credentials_exception):
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])

    try:
        id = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = classes.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data # Return ID

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not verify credentials.', headers={"WWW-Authentication": "Bearer"})

    token = verify_token(token, credentials_exception)

    cursor.execute(""" SELECT * FROM users
                       WHERE id = %s; """, (token.id,))
    
    return cursor.fetchone()