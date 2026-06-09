import uuid 
from datetime import datetime

from fastapi_users import schemas 
from pydantic import ConfigDict

class UserRead(schemas.BaseUser[uuid.UUID]):
    # BaseUser provides: id, email, is_active, is_superuser, is_verified
    model_config = ConfigDict(from_attributes=True)
    role: str 
    created_at: datetime

class UserCreate(schemas.BaseUserCreate):
    # BaseUserCreate provides: email, password (+ optional flags)
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass