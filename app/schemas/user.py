import uuid

from sqlmodel import SQLModel


class UserPublic(SQLModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool


class UserUpdate(SQLModel):
    full_name: str | None = None
    is_active: bool | None = None
