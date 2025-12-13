from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from datetime import datetime
from fastapi import File, UploadFile, Form
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from database import Base, engine, SessionLocal
import models
import schemas
import auth
import math
import uuid

# Buat semua tabel di database (sekali di awal)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

OFFICE_LAT = -6.175392   # contoh: Monas (ganti ke koordinat kantor kamu)
OFFICE_LNG = 106.827153
OFFICE_RADIUS_M = 150    # radius sah (meter)
MAX_ACCURACY_M = 200     # kalau GPS akurasinya jelek banget, tolak

UPLOAD_DIR = Path("uploads/selfies")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

security = HTTPBearer()

# Izinkan Frontend melalui vite mengakses backend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], #asal mana saja yang diizinkan
    allow_credentials=True,
    allow_methods=["*"], #metode apa saja (GET, POST PUT ,DLL)
    allow_headers=["*"], #header apa saja yang boleh
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):     
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = creds.credentials
    
    try:
        payload = auth.decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_admin(current_user: models.Users = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Hitung jarak 2 koordinat (meter) pakai rumus Haversine.
    """
    R = 6371000  # radius bumi meter
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def build_selfie_url(path: str | None) -> str | None:
    if not path:
        return None
    # path kamu: "uploads/selfies/xxx.jpg"
    # setelah mount, URL-nya: "/uploads/selfies/xxx.jpg"
    return "/" + path.replace("\\", "/").lstrip("/")

def to_attendance_read(att: models.Attendance) -> dict:
    return {
        "id": att.id,
        "user_id": att.user_id,
        "check_in_at": att.check_in_at,
        "check_out_at": att.check_out_at,
        "status": att.status,

        "lat": att.lat,
        "lng": att.lng,
        "accuracy_m": att.accuracy_m,
        "distance_m": att.distance_m,
        "is_valid_location": att.is_valid_location,
        "selfie_path": att.selfie_path,

        "check_out_lat": att.check_out_lat,
        "check_out_lng": att.check_out_lng,
        "check_out_accuracy_m": att.check_out_accuracy_m,
        "check_out_distance_m": att.check_out_distance_m,
        "check_out_is_valid_location": att.check_out_is_valid_location,
        "check_out_selfie_path": att.check_out_selfie_path,

        "selfie_url": build_selfie_url(att.selfie_path),
        "check_out_selfie_url": build_selfie_url(att.check_out_selfie_path),
    }

@app.get("/")
def test():
    return {"Message": "Hello from backend"}

@app.post("/debug/create-sample-user")
def create_sample_user(db: Session = Depends(get_db)):
    user = models.Users(
        name="Budi Sample",
        email="budi@example.com",
        password_hash="dummy",
        role = "STAFF",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return{
        "id" : user.id,
        "name" : user.name,
        "email" : user.email,
        "role" : user.role,
    }

@app.get("/debug/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.Users).all()
    # Convert ke dict biar gampang di-JSON-kan  
    return [
        {
            "id": u.id,
            "name" : u.name,
            "email" : u.email,
            "role" : u.role,
        }
        for u in users
    ]

@app.post("/auth/register", response_model=schemas.UserRead)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    #cek email apakah sudah terdaftar atau belom
    existing = db.query(models.Users).filter(models.Users.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )

    #hash password
    hashed_password = auth.get_password_hash(user_in.password)

    user = models.Users(
        name = user_in.name,
        email= user_in.email,
        password_hash = hashed_password,
        role = user_in.role
    )

    #Simpan ke database 
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@app.post("/auth/login", response_model=schemas.Token)
def login(login_in: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.email == login_in.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Email atau password salah")

    if not auth.verify_password(login_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserRead)
def me(current_user: models.Users = Depends(get_current_user)):
    return current_user

@app.post("/attendance/check-in", response_model=schemas.AttendanceRead)
def check_in(
    lat: float = Form(...),
    lng: float = Form(...),
    accuracy_m: float | None = Form(None),
    selfie: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user),
):
    # 1) Anti double check-in
    open_att = (
        db.query(models.Attendance)
        .filter(models.Attendance.user_id == current_user.id)
        .filter(models.Attendance.check_out_at.is_(None))
        .first()
    )
    if open_att:
        raise HTTPException(status_code=400, detail="Kamu masih check-in (belum check-out).")

    # 2) Validasi file selfie
    if selfie.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Selfie harus JPG/PNG.")

    # 3) Validasi accuracy
    if accuracy_m is not None and accuracy_m > MAX_ACCURACY_M:
        raise HTTPException(status_code=400, detail="GPS tidak akurat, coba ulangi.")

    # 4) Hitung jarak
    dist = haversine_m(lat, lng, OFFICE_LAT, OFFICE_LNG)
    if dist > OFFICE_RADIUS_M:
        raise HTTPException(status_code=400, detail=f"Di luar area kantor (jarak {dist:.1f}m).")

    # 5) Simpan file selfie
    ext = ".jpg" if selfie.content_type == "image/jpeg" else ".png"
    filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(selfie.file.read())

    # 6) Simpan Attendance
    att = models.Attendance(
        user_id=current_user.id,
        status="ON_TIME",
        lat=lat,
        lng=lng,
        accuracy_m=accuracy_m,
        distance_m=dist,
        is_valid_location=True,
        selfie_path=str(filepath).replace("\\", "/"),
    )

    db.add(att)
    db.commit()
    db.refresh(att)
    return to_attendance_read(att)


@app.post("/attendance/check-out", response_model=schemas.AttendanceRead)
def check_out(
    lat: float = Form(...),
    lng: float = Form(...),
    accuracy_m: float | None = Form(None),
    selfie: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user),
):
    open_att = (
        db.query(models.Attendance)
        .filter(models.Attendance.user_id == current_user.id)
        .filter(models.Attendance.check_out_at.is_(None))
        .first()
    )
    if not open_att:
        raise HTTPException(status_code=400, detail="Tidak ada check-in yang aktif untuk di-check-out.")

    # Validasi file
    if selfie.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Selfie harus JPG/PNG.")

    # Validasi accuracy
    if accuracy_m is not None and accuracy_m > MAX_ACCURACY_M:
        raise HTTPException(status_code=400, detail="GPS tidak akurat, coba ulangi.")

    # Validasi radius kantor (sama seperti check-in)
    dist = haversine_m(lat, lng, OFFICE_LAT, OFFICE_LNG)
    if dist > OFFICE_RADIUS_M:
        raise HTTPException(status_code=400, detail=f"Di luar area kantor (jarak {dist:.1f}m).")

    # Simpan selfie check-out
    ext = ".jpg" if selfie.content_type == "image/jpeg" else ".png"
    filename = f"{current_user.id}_out_{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(selfie.file.read())

    # Update attendance
    open_att.check_out_at = datetime.utcnow()
    open_att.check_out_lat = lat
    open_att.check_out_lng = lng
    open_att.check_out_accuracy_m = accuracy_m
    open_att.check_out_distance_m = dist
    open_att.check_out_is_valid_location = True
    open_att.check_out_selfie_path = str(filepath).replace("\\", "/")

    db.commit()
    db.refresh(open_att)
    return to_attendance_read(open_att)

@app.get("/attendance/me", response_model=list[schemas.AttendanceRead])
def my_attendance(
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(get_current_user),
):
    rows = (
        db.query(models.Attendance)
        .filter(models.Attendance.user_id == current_user.id)
        .order_by(models.Attendance.check_in_at.desc())
        .all()
    )
    return [to_attendance_read(x) for x in rows]

@app.get("/admin/attendance", response_model=list[schemas.AttendanceRead])
def admin_list_attendance(
    db: Session = Depends(get_db),
    admin: models.Users = Depends(require_admin),
):
    rows = db.query(models.Attendance).order_by(models.Attendance.check_in_at.desc()).limit(50).all()
    return [to_attendance_read(x) for x in rows]

@app.get("/admin/users", response_model=list[schemas.UserRead])
def admin_list_users(
    db: Session = Depends(get_db),
    admin: models.Users = Depends(require_admin),
):
    users = db.query(models.Users).order_by(models.Users.id.asc()).all()
    return users

@app.patch("/admin/users/{user_id}/role", response_model=schemas.UserRead)
def admin_update_user_role(
    user_id: int,
    payload: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    admin: models.Users = Depends(require_admin),
):
    role = payload.role.upper()
    if role not in ["STAFF", "ADMIN"]:
        raise HTTPException(status_code=400, detail="role harus STAFF atau ADMIN")
    
    if user.id == admin.id and role != "ADMIN":
        raise HTTPException(status_code=400, detail="Tidak boleh menurunkan role akun admin sendiri.")

    user = db.query(models.Users).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    user.role = role
    db.commit()
    db.refresh(user)
    return user