# Handles user authentication

from fastapi import status, HTTPException, APIRouter
from .. import classes, utils, dbConnection, oauth2

router = APIRouter(tags=['Authentication'])
cursor = dbConnection.cursor

@router.post('/login', response_model=classes.Token)
def login(credentials: classes.User):
    cursor.execute(""" SELECT * FROM users
                       WHERE email = %s; """, (credentials.email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
        f"Invalid Credentials.")

    # Checks if user entered correct password
    if not utils.checkPassword(credentials.password, user['password']):
        raise HTTPException(status.HTTP_403_FORBIDDEN,
        f"Invalid Credentials.")

    # User is verified at this point
    # Generate JWT token to authenticate user for API access
    access_token = oauth2.create_access_token(data={"user_id": user['id']})
    access_token = classes.Token(token=access_token, token_type='Bearer')

    return access_token