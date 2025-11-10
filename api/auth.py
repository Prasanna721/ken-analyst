import hashlib
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import API_SECRET

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    expected_hash = hashlib.sha256(API_SECRET.encode()).hexdigest()

    if token != expected_hash:
        raise HTTPException(status_code=403, detail="Invalid token")
    return True
