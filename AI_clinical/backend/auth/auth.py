from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict

SECRET_KEY = "fastapi"
EXPIRE_TIME = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def create_access_token(data: Dict) -> str:
    encode_text = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_TIME)
    encode_text.update({"exp": expire})
    return jwt.encode(encode_text, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[Dict]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "user_id": payload.get("user_id")
        }
    except JWTError:
        return None

def require_auth(current_user: Optional[Dict] = Depends(get_current_user)) -> Dict:
    if not current_user:
        raise HTTPException(401, "Invalid authentication credentials")
    return current_user

def require_admin(current_user: Dict = Depends(require_auth)) -> Dict:
    if current_user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return current_user

def require_doctor(current_user: Dict = Depends(require_auth)) -> Dict:
    if current_user.get("role") != "doctor":
        raise HTTPException(403, "Doctor access required")
    return current_user