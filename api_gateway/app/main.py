from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel
from api.services.email import email
from api.services.tuition import tution
from api.services.user import user
from api.services.transaction import transaction
import bcrypt
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.models import UserLogin, Token
from api.db import authenticateCollection
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
USER_SERVICE_HOST = os.getenv("USER_SERVICE_HOST")
# FRONT_END_URL = os.getenv("FRONT_END_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cho phép truy cập từ domain này
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_user(username: str):
    user = authenticateCollection.find_one({"username": username})
    if user:
        return UserLogin(**user)

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # user = get_user(username)
        # if user is None:
        #     raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# API endpoints
@app.post("/user/add")
async def add_user(user: UserLogin):
    user.hashed_password = hash_password(user.hashed_password)
    try:
        result = authenticateCollection.insert_one(user.model_dump())
        # Check if the insert operation was acknowledged by MongoDB
        if result.acknowledged:
            return {"message": "User added successfully"}
        else:
            raise HTTPException(status_code=500, detail="User could not be added")
    except Exception as e:
        # Log the error here or perform further error handling
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/me")
async def get_current_username(current_username: str = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_HOST}/user/{current_username}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

app.include_router(user, tags=["user service"], dependencies=[Depends(oauth2_scheme)])
app.include_router(email, tags=["email service"], dependencies=[Depends(oauth2_scheme)])
app.include_router(tution, tags=["tution service"], dependencies=[Depends(oauth2_scheme)])
app.include_router(transaction, tags=["transaction service"], dependencies=[Depends(oauth2_scheme)])

