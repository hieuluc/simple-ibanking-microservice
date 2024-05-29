from fastapi import FastAPI
from api.tuitions import tutions

app = FastAPI()
app.include_router(tutions, prefix="/api/v1", tags=["tuitions"])