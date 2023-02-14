from .. import classes, dbConnection, oauth2
from fastapi import status, HTTPException, APIRouter, Depends
from .posts import find_post

router = APIRouter(
    prefix = '/vote',
    tags = ['Vote']
)

cursor = dbConnection.cursor
connection = dbConnection.connection

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: classes.Vote, current_user: classes.User = Depends(oauth2.get_current_user)):
    if not find_post(vote.post_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND,
        f"This post does not exist.")

    found_vote = find_vote(vote.post_id, current_user['id'])
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status.HTTP_409_CONFLICT,
            'You don like am already ah. No dey simp.')

        cursor.execute(""" INSERT INTO votes (post_id, user_id)
                            VALUES (%s, %s) """, (vote.post_id, current_user['id']))
        connection.commit()

        return {'detail': f"User #{current_user['id']} liked post #{vote.post_id}"}
            
    elif vote.dir == 0:
        if not found_vote:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
            f"You have not voted on this post.")

        cursor.execute(""" DELETE FROM votes
                           WHERE post_id = %s AND user_id = %s """, (vote.post_id, current_user['id']))
        connection.commit()

        return {'detail': f"User #{current_user['id']} removed their like from post #{vote.post_id}"}
        
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
        f"Invalid vote type.")

def find_vote(post_id, user_id):
    cursor.execute(""" SELECT * FROM votes
                       WHERE user_id = %s AND post_id = %s; """, (user_id, post_id))

    return cursor.fetchone()