from fastapi import FastAPI
from api.users import users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8005/"],  # cho phép truy cập từ domain này
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

app.include_router(users,  prefix="/api/v1", tags=["users"])