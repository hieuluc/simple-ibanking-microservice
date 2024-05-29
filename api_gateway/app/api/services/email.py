import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import httpx
from ..models import OTP, OTPVerify, Email

email = APIRouter()

load_dotenv()
EMAIL_SERVICE_HOST = os.getenv("EMAIL_SERVICE_HOST")

@email.post("/send-otp/")
async def gateway_send_otp(request: OTP):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service3:8000/api/v1/send-otp/", json=request.dict())
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


@email.post("/verify-otp/")
async def gateway_verify_otp(request: OTPVerify):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service3:8000/api/v1/verify-otp/", json=request.dict())
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


@email.post("/send-email/")
async def gateway_send_email(request: Email):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service3:8000/api/v1/send-email/", json=request.dict())
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
