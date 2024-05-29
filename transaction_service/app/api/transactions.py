import datetime
from fastapi import APIRouter, HTTPException
from .models import Payment, Account, VerifyAndProcessPaymentRequest
from .db import paymentsCollection, accountsCollection, historysCollection
import httpx

transaction = APIRouter()

@transaction.post("/process-tuition/")
async def process_tuition(username: str, receiver: str):
    # 1. Lấy version từ Payment theo receiver
    payment = paymentsCollection.find_one({"username": receiver})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found. Please try confirm again.")
    version = payment.get("version", 0)
    
    # 2. Gọi API tuition và so sánh với bal trong Account của username
    async with httpx.AsyncClient() as client:
        tuition_response = await client.get(f"http://service2:8000/api/v1/tuition/{receiver}")
        tuition_response = tuition_response.json()

    account = accountsCollection.find_one({"username": username})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found. Please try confirm again.")
    
    tuition_fee = tuition_response.get("tuition_fee")
    bal = account.get("bal")
    
    # 3. So sánh và gửi OTP nếu thỏa mãn
    if tuition_fee < bal:
        receiver_email = account.get("email")
        # Gọi API để gửi OTP
        async with httpx.AsyncClient() as client:
            otp_response = await client.post(
                "http://service3:8000/api/v1/send-otp/",
                json={"receiver_email": receiver_email}
            )
            otp_response = otp_response.json()
            print(otp_response)
        
        # 4. Kiểm tra response và trả về version nếu thành công
        if otp_response.get("status_code") == 200:
            return {"version": version}
        else:
            raise HTTPException(status_code=otp_response.get("status_code", 500), detail="Failed to send OTP. Please try confirm again.")
    else:
        raise HTTPException(status_code=400, detail="Tuition fee is not less than balance. Please try confirm again.")
    
@transaction.post("/verify-and-process-payment/")
async def verify_and_process_payment(request: VerifyAndProcessPaymentRequest):
    # 1. Gọi API để xác thực OTP
    async with httpx.AsyncClient() as client:
        otp_response = await client.post(
            "http://service3:8000/api/v1/verify-otp/",
            json={"email": request.email, "otp": request.otp}
        )
        otp_response = otp_response.json()

        if not otp_response.get("valid"):
            raise HTTPException(status_code=400, detail="OTP verification failed. ")

    # 2. Kiểm tra và cập nhật version trong paymentsCollection
    payment_query = {"username": request.receiver, "version": request.version}
    updated_payment = paymentsCollection.find_one_and_update(
        payment_query,
        {"$inc": {"version": 1}}, # Tăng version lên 1
        return_document=True
    )
    if not updated_payment:
        raise HTTPException(status_code=400, detail="The transaction failed, someone has already paid this student.")

    # 3. Cập nhật bal trong accountsCollection
    account_query = {"username": request.username}
    updated_account = accountsCollection.find_one_and_update(
        account_query,
        {"$inc": {"bal": - request.amount}}, # Giảm balance đi amount
        return_document=True
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 4. Gạch nợ và gửi email thông báo thành công
    async with httpx.AsyncClient() as client:
        # Gạch nợ
        response = await client.patch(f"http://service2:8000/api/v1/tuition/{request.receiver}/update-fee-paid",
            json=True
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to update tuition fee paid")
            
        # Gửi mail thông báo
        try:
            response = await client.post(
            "http://service3:8000/api/v1/send-email/",
            json={
                "receiver_email": request.email,
                "subject": "successful transaction",
                "message": "Your transaction has been successfully processed."
            }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Failed to send email")
    # 5. Lưu lịch sử giao dịch
    historysCollection.insert_one({
        "username": request.username,
        "receiver": request.receiver,
        "amount": request.amount,
        "date": datetime.datetime.now()
    })

    return {"message": "Transaction successfully processed"}

# Endpoint tạo mới Account
@transaction.post("/accounts/")
def create_account(account: Account):
    if accountsCollection.find_one({"username": account.username}):
        raise HTTPException(status_code=400, detail="Account already exists")
    accountsCollection.insert_one(account.dict())
    return {"message": "Account created successfully"}

# Endpoint tạo mới Payment
@transaction.post("/payments/")
def create_payment(payment: Payment):
    if paymentsCollection.find_one({"username": payment.username}):
        raise HTTPException(status_code=400, detail="Payment entry already exists")
    paymentsCollection.insert_one(payment.dict())
    return {"message": "Payment created successfully"}

@transaction.get("/get-balance/{username}")
async def get_balance(username: str):
    account_data = accountsCollection.find_one({"username": username})
    if account_data:
        return {"username": account_data["username"], "bal": account_data["bal"]}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@transaction.get("/history/{username}")
async def get_history(username: str):
    history_data = historysCollection.find({"username": username}).sort("date", -1)
    if history_data:
        # Chuyển từ cursor của MongoDB thành list các documents
        history_list = list(history_data)
        # Định dạng lại dữ liệu trước khi trả về (ví dụ: loại bỏ ObjectId)
        for item in history_list:
            item['_id'] = str(item['_id'])  # Chuyển ObjectId thành string để JSON có thể serialize
            item['date'] = item['date'].isoformat()  # Chuyển datetime thành string ISO format
        return history_list
    else:
        # Nếu không tìm thấy, trả về thông báo lỗi
        raise HTTPException(status_code=404, detail="No history found for this user")