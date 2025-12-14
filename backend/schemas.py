from pydantic import BaseModel, EmailStr, ConfigDict, constr
from datetime import datetime
from typing import Optional

selfie_path: Optional[str] = None

# Schema: input untuk register user
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "STAFF" #defaultnya ini, bisa diatur nanti.

# Schema: output (response) ke client (tanpa password)
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AttendanceRead(BaseModel):
    id: int
    user_id: int
    check_in_at: datetime
    check_out_at: Optional[datetime] = None
    status: str

    lat: Optional[float] = None
    lng: Optional[float] = None
    accuracy_m: Optional[float] = None
    distance_m: Optional[float] = None
    is_valid_location: bool

    selfie_path: str | None = None

    check_out_lat: float | None = None
    check_out_lng: float | None = None
    check_out_accuracy_m: float | None = None
    check_out_distance_m: float | None = None
    check_out_is_valid_location: bool = False
    check_out_selfie_path: str | None = None

    selfie_url: str | None = None
    check_out_selfie_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class AttendanceCheckInRequest(BaseModel):
    lat: float
    lng: float
    accuracy_m: float | None = None

class ResetPasswordIn(BaseModel):
    new_password: constr(min_length=6, max_length=72)