from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., unique=True)
    full_name: str = None
    phone: str = None
    email: str = None