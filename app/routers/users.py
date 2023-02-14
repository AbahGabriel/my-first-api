from .. import classes, utils, dbConnection, oauth2
from fastapi import status, HTTPException, APIRouter
from typing import List

router = APIRouter(
    prefix='/users',
    tags=['Users']
) # Allows main API instance to use this file

cursor = dbConnection.cursor # Gives router access to the database connection
connection = dbConnection.connection

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=classes.UserResponse)
def create_user(user: classes.User):
    # Hash user's password
    user.password = utils.hash(user.password)

    # Add new user to data source, with their hashed password
    cursor.execute(""" INSERT INTO users (email, password)
                       VALUES (%s, %s) """, (user.email, user.password))
    connection.commit()

    # Retrieves inserted user
    lastIdInserted = cursor.lastrowid
    new_user = find_user(lastIdInserted)

    return new_user

@router.get("/get", response_model=List[classes.UserResponse])
def get_users():
    cursor.execute(""" SELECT * FROM users; """) # Pass in query
    users = cursor.fetchall() # Get query results

    if len(users) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"No users were found. Create a post and it will routerear here.")
    
    return users

@router.get("/get/{id}", response_model=classes.UserResponse)
def get_user(id: int):
    user = find_user(id)

    # Raises 404 Error if post is not found
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"User with id #{id} was not found.")

    return user

@router.put("/update/{id}", response_model=classes.UserResponse)
def update_user(id: int, user: classes.User):
    if not find_user(id):
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"User with id #{id} was not found.")

    # Update row based on id
    cursor.execute(""" UPDATE users
                        SET email = %s, password = %s
                        WHERE id = %s """, (user.email, user.password, id))
    connection.commit()
    new_user = find_user(id)

    return new_user

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    if not find_user(id):
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"User with id #{id} was not found.")

    cursor.execute(""" DELETE FROM users
                       WHERE id = %s; """, (id,))
    connection.commit()

def find_user(id):
    cursor.execute(""" SELECT * FROM users
                       WHERE id = %s; """, (id,))
    
    return cursor.fetchone()