from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

SUPERADMIN_ROLE_ID = "founder"

class UserBase(BaseModel):
    email: EmailStr
    role_id: str = Field(..., description="References the dynamic role ID")
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    scopes: List[str] = []

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str