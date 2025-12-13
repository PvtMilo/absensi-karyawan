from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.sql import func
from database import Base

# Table users 
class Users(Base):
    __tablename__ = "users"  # nama table di database

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # typo diperbaiki
    role = Column(String, nullable=False, default="STAFF")
    created_at = Column(DateTime, server_default=func.now())

# Table attendance
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    check_in_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    check_out_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String, nullable=False, default="ON_TIME")

    # ===== CHECK-IN GPS =====
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    accuracy_m = Column(Float, nullable=True)

    distance_m = Column(Float, nullable=True)
    is_valid_location = Column(Boolean, default=False)

    # ===== CHECK-IN SELFIE =====
    selfie_path = Column(Text, nullable=True)

    # ===== CHECK-OUT GPS =====
    check_out_lat = Column(Float, nullable=True)
    check_out_lng = Column(Float, nullable=True)
    check_out_accuracy_m = Column(Float, nullable=True)

    check_out_distance_m = Column(Float, nullable=True)
    check_out_is_valid_location = Column(Boolean, default=False)

    # ===== CHECK-OUT SELFIE =====
    check_out_selfie_path = Column(Text, nullable=True)

