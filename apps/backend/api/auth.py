import jwt
from django.conf import settings
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            decoded = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=["HS256"], 
                audience="authenticated", 
                issuer=settings.JWT_ISSUER
            )
            return decoded
        except jwt.PyJWTError:
            return None
