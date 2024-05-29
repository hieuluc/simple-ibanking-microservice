import datetime
import random
import smtplib
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException
from .models import Email, OTP, OTPVerify
from .db import otpsCollection

load_dotenv()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EXPIRE_OTP = os.getenv("EXPIRE_OTP")

# Ensure the collection uses a TTL index to auto-delete documents after 60 seconds
otpsCollection.create_index("expire_at", expireAfterSeconds=int(EXPIRE_OTP))

email = APIRouter()
def generate_otp():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

@email.post("/send-otp/")
async def send_otp(request: OTP):
    # Check if an active OTP already exists for the user
    if otpsCollection.find_one({"email": request.receiver_email}):
        return HTTPException(status_code=400, detail="An active OTP already exists for this user, please wait for " + str((float(EXPIRE_OTP)/60)) + " minute before requesting a new OTP.")
    otp = generate_otp()
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=float(EXPIRE_OTP))
    # Save OTP to MongoDB
    otpsCollection.insert_one({
        "email": request.receiver_email,
        "otp": otp,
        "expire_at": expire_at
    })

    sender_email = "hieuluc.test@gmail.com"
    subject = "OTP iBanking Microservice"
    message = f"Your OTP is: {otp}"
    email_text = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, EMAIL_PASSWORD)
        server.sendmail(sender_email, request.receiver_email, email_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        server.quit()

    return HTTPException(status_code=200, detail="OTP sent successfully")

@email.post("/verify-otp/")
async def verify_otp(request: OTPVerify):
    # Find and delete the OTP for the given email if it matches
    query = {"email": request.email, "otp": request.otp}
    otp_record = otpsCollection.find_one_and_delete(query)
    if otp_record:
        return {"valid": True}
    else:
        return {"valid": False}

@email.post("/send-email/")
async def send_email(email_details: Email):
    sender_email = "hieuluc.test@gmail.com"
    email_text = f"Subject: {email_details.subject}\n\n{email_details.message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, EMAIL_PASSWORD)
        server.sendmail(sender_email, email_details.receiver_email, email_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        server.quit()
    
    return {"message": "Email sent successfully to", "receiver": email_details.receiver_email}
