from fastapi import FastAPI
from api.email import email

app = FastAPI()

app.include_router(email,  prefix="/api/v1", tags=["send email"])