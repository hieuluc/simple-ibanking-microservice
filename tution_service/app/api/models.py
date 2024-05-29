from pydantic import BaseModel

class Tuition(BaseModel):
    username: str
    full_name: str = None
    tuition_fee: float = 0.0
    fee_paid: bool = False
    