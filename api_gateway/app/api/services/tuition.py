import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Body, HTTPException
import httpx
from ..models import Tuition

tution = APIRouter()

load_dotenv()
TUTION_SERVICE_HOST = os.getenv("EMAIL_SERVICE_HOST")


@tution.post("/tuition", response_model=Tuition)
async def gateway_add_tuition(tuition: Tuition):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service2:8000/api/v1/tuition", json=tuition.model_dump())
        if resp.status_code != 200:
            # Giải mã JSON từ phản hồi để tránh "bọc" không mong muốn
            detail = resp.json().get('detail', '{}')
            try:
                # Cố gắng phân tích cú pháp detail xem nó có phải là JSON không
                detail_json = json.loads(detail)
                if 'detail' in detail_json:
                    detail = detail_json['detail']
            except json.JSONDecodeError:
                # Nếu không phân tích cú pháp được, giữ nguyên detail
                pass
            raise HTTPException(status_code=resp.status_code, detail=detail)
        return resp.json()


@tution.get("/tuition/{username}", response_model=Tuition)
async def gateway_get_tuition_by_username(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://service2:8000/api/v1/tuition/{username}")
        if resp.status_code != 200:
            # Giải mã JSON từ phản hồi để tránh "bọc" không mong muốn
            detail = resp.json().get('detail', '{}')
            try:
                # Cố gắng phân tích cú pháp detail xem nó có phải là JSON không
                detail_json = json.loads(detail)
                if 'detail' in detail_json:
                    detail = detail_json['detail']
            except json.JSONDecodeError:
                # Nếu không phân tích cú pháp được, giữ nguyên detail
                pass
            raise HTTPException(status_code=resp.status_code, detail=detail)
        return resp.json()


@tution.patch("/tuition/{username}/update-fee-paid")
async def gateway_update_fee_paid(username: str, fee_paid: bool = Body(...)):
    async with httpx.AsyncClient() as client:
        resp = await client.patch(f"http://service2:8000/api/v1/tuition/{username}/update-fee-paid", json=fee_paid)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.text