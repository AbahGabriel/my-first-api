# Helper methods for specific tasks

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash(password: str):
    return pwd_context.hash(password)

def checkPassword(plainPassword: str, hashedPassword: str):
    return pwd_context.verify(plainPassword, hashedPassword)