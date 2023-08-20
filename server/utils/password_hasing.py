from passlib.context import CryptContext

__all__ = ["Hash"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def bcrypt(password: str):
        return pwd_context.hash(password)
