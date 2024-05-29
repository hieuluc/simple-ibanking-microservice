from pydantic import BaseModel, Field

# Authenticate
class UserLogin(BaseModel):
    username: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
        
# Email Service
class OTP(BaseModel):
    receiver_email: str


class OTPVerify(BaseModel):
    email: str
    otp: str


class Email(BaseModel):
    receiver_email: str
    subject: str
    message: str

# Tuition Service
class Tuition(BaseModel):
    username: str
    full_name: str = None
    tuition_fee: float = 0.0
    fee_paid: bool = False
    
# User Service
class User(BaseModel):
    username: str = Field(..., unique=True)
    full_name: str = None
    phone: str = None
    email: str = None
    
# Transaction Service
class Payment(BaseModel):
    username: str
    email: str
    version: int = 0
    
class Account(BaseModel):
    username: str
    email: str
    bal: float
    
class ProcessTuitionRequest(BaseModel):
    username: str
    receiver: str

class VerifyAndProcessPaymentRequest(BaseModel):
    version: int
    otp: str
    username: str
    email: str
    receiver: str
    amount: float