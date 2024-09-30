from pydantic import BaseModel # type: ignore

class EmailOrder(BaseModel):
    store_id: str
    order_id: str
    user_id: str
    path: str

class EmailTest(BaseModel):
    user_id: str
    store_id: str
    test_email: str

