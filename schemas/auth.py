from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str = "Admin"
    password: str = "Admin"
