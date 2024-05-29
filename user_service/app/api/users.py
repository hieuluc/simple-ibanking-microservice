from fastapi import APIRouter, HTTPException
from .models import User
from .db import usersCollection

users = APIRouter()

@users.get("/user/{username}", response_model=User)
async def get_user_by_username(username: str):
    user_data = usersCollection.find_one({"username": username})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_data)