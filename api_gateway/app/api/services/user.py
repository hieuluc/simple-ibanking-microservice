import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import httpx
from ..models import User

user = APIRouter()

load_dotenv()
USER_SERVICE_HOST = os.getenv("USER_SERVICE_HOST")


@user.get("/user/{username}", response_model=User)
async def gateway_get_user_by_username(username: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://service1:8000/api/v1/user/{username}")
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