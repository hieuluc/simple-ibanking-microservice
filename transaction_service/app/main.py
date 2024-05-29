from fastapi import FastAPI
from api.transactions import transaction

app = FastAPI()

app.include_router(transaction,  prefix="/api/v1", tags=["transaction"])