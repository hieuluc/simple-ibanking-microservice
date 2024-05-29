from pydantic import BaseModel

class Payment(BaseModel):
    username: str
    email: str
    version: int = 0
    
class Account(BaseModel):
    username: str
    email: str
    bal: float
    
class VerifyAndProcessPaymentRequest(BaseModel):
    version: int
    otp: str
    username: str
    email: str
    receiver: str
    amount: float