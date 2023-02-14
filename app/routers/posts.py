from .. import classes, utils, dbConnection, oauth2
from fastapi import status, HTTPException, APIRouter, Depends
from typing import List
from .users import find_user

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
) # Allows main API instance to use this file

cursor = dbConnection.cursor # Gives router access to the database connection
connection = dbConnection.connection

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=classes.PostResponse)
def create_post(post: classes.Post, current_user: classes.User = Depends(oauth2.get_current_user)):
    cursor.execute(""" INSERT INTO posts (title, content, published, user_id)
                       VALUES (%s, %s, %s, %s) """,
                       (post.title, post.content, post.published, current_user['id']))
    connection.commit()

    # Retrieves inserted post
    lastIdInserted = cursor.lastrowid
    new_post = find_post(lastIdInserted)

    return new_post

@router.get("/get", response_model=List[classes.PostResponse])
def get_posts(search: str = '%', limit: int = 10, skip: int = 0):
    cursor.execute(f""" SELECT * FROM posts
                        WHERE title LIKE '%{search}%'
                        LIMIT %s OFFSET %s; """, (limit, skip))
    posts = cursor.fetchall()

    if len(posts) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"No posts were found. Create a post and it will appear here.")

    for post in posts:
        post['user'] = find_user(post['user_id'])
        post['votes'] = get_like_count(post['id'])
    
    return posts

@router.get("/get/{id}", response_model=classes.PostResponse)
def get_post(id: int):
    post = find_post(id)

    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"Post with id #{id} was not found.")

    post['user'] = find_user(post['user_id'])
    post['votes'] = get_like_count(post['id'])

    return post

@router.put("/update/{id}", response_model=classes.PostResponse)
def update_post(id: int, post: classes.Post, current_user: classes.User = Depends(oauth2.get_current_user)):
    post = find_post(id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"Post with id #{id} was not found.")

    if post['user_id'] != current_user['id']:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
        f"You can only update your own posts bro. Be civil.")

    cursor.execute(""" UPDATE posts
                       SET title = %s, content = %s, published = %s
                       WHERE id = %s """, (post.title, post.content, post.published, id))
    connection.commit()
    new_post = find_post(id) # Return updated post

    return new_post

@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int, current_user: classes.User = Depends(oauth2.get_current_user)):

    post = find_post(id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"Post with id #{id} was not found.")

    if post['user_id'] != current_user['id']:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
        f"You can only delete your own posts bro. Be civil.")

    cursor.execute(""" DELETE FROM posts
                       WHERE id = %s; """, (id,))
    connection.commit()

def find_post(id):
    cursor.execute(""" SELECT * FROM posts
                       WHERE id = %s; """, (id,))
    
    return cursor.fetchone()

def get_like_count(id):
    cursor.execute(""" SELECT COUNT(post_id) FROM votes
                       WHERE post_id = %s; """, (id,))

    result = cursor.fetchone()
    return result['COUNT(post_id)']
