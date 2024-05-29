import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import httpx
from ..models import Account, Payment, ProcessTuitionRequest, VerifyAndProcessPaymentRequest

transaction = APIRouter()

load_dotenv()
TRANSACTION_SERVICE_HOST = os.getenv("TRANSACTION_SERVICE_HOST")


@transaction.post("/process-tuition/")
async def gateway_process_tuition(username: str, receiver: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service4:8000/api/v1/process-tuition/?username={username}&receiver={receiver}")
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



@transaction.post("/verify-and-process-payment/")
async def gateway_verify_and_process_payment(request: VerifyAndProcessPaymentRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service4:8000/api/v1/verify-and-process-payment/", json=request.dict())
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


@transaction.post("/accounts/")
async def gateway_create_account(account: Account):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service4:8000/api/v1/accounts/", json=account.dict())
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


@transaction.post("/payments/")
async def gateway_create_payment(payment: Payment):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"http://service4:8000/api/v1/payments/", json=payment.model_dump())
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
    
@transaction.get("/get-balance/{username}")
async def get_balance(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://service4:8000/api/v1/get-balance/{username}")
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

@transaction.get("/history/{username}")
async def get_history(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://service4:8000/api/v1/history/{username}")
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