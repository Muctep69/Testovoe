from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: int
    username: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

    password: Optional[str] = None
class NoteBase(BaseModel):
    title: Optional[str]
    content: Optional[str]

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):

    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]=None
    user_id: int

    class Config:
        from_attributes = True

