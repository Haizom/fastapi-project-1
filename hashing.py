from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def hash(password):
        hashed_password = pwd_context.hash(password)
        return hashed_password
    
    def verifyPass(plain, hashed):
        return pwd_context.verify(plain, hashed)