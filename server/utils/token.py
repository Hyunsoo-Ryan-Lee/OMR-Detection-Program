import jwt
from datetime import datetime, timedelta

__all__ = ["create_access_token"]

JWT_SECRET = "1q2w3e4r!@#"
JWT_ALGORITHM = "HS256"


def create_access_token(*, data: dict = None):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# def create_access_token(*, data: dict = None, expires_delta: int = None):
#     to_encode = data.copy()
#     if expires_delta:
#         to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return encoded_jwt
