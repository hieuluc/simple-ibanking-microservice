from fastapi import APIRouter, Body, HTTPException
from .models import Tuition
from .db import tutionsCollection

tutions = APIRouter()

@tutions.post("/tuition", response_model=Tuition)
async def add_tuition(tuition: Tuition):
    if tutionsCollection.find_one({"username": tuition.username}):
        raise HTTPException(status_code=400, detail="Tuition for this username already exists")
    
    # chuyển model Pydantic về dạng dictionary trước khi lưu vào MongoDB
    tuition_data = tuition.model_dump()
    result = tutionsCollection.insert_one(tuition_data)
    
    # Lấy lại bản ghi vừa được thêm để trả về
    created_tuition = tutionsCollection.find_one({"_id": result.inserted_id})
    return Tuition(**created_tuition)



@tutions.get("/tuition/{username}", response_model=Tuition)
async def get_tuition_by_username(username: str):
    tuition_data = tutionsCollection.find_one({"username": username})
    if tuition_data is None:
        raise HTTPException(status_code=404, detail="Tuition information not found")
    return Tuition(**tuition_data)

from fastapi import Response

@tutions.patch("/tuition/{username}/update-fee-paid")
async def update_fee_paid(username: str, fee_paid: bool = Body(...)):
    updated_result = tutionsCollection.update_one({"username": username}, {"$set": {"fee_paid": fee_paid}})
    if updated_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Tuition information not found or update failed")
    return Response(content="Successfully updated fee paid status", status_code=200)