import datetime
from pydantic import BaseModel

class Email(BaseModel):
    receiver_email: str
    subject: str
    message: str
    
class OTP(BaseModel):
    receiver_email: str

class OTPVerify(BaseModel):
    email: str
    otp: str