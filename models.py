from pydantic import BaseModel, EmailStr, validator
from fastapi import HTTPException, status
from typing import Optional


class User(BaseModel):
    first_name : str
    last_name : str
    email : EmailStr
    username : str
    password : str
    confirm_password : str

    @validator("confirm_password", pre=True, always = True)
    def validate_password(cls, confirm_password, values):
        password = values.get('password')
        if password != confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password doesnt match!")
            
        return confirm_password
        
class ShowUser(BaseModel):
    first_name : str
    last_name : str
    email : EmailStr
    username : str

class Login(BaseModel):
    username: str
    password: str


