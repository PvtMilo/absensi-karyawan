from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base

#Lokasi dari db (sekarang di root backend folder)
SQLALCHEMY_DATABASE_URL = "sqlite:///./absensi.db"

#Engine: koneksi utama ke database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread" : False}, #khusus SQLite di FastAPI
)

# SessionLocal: "pabrik" untuk bikin session (koneksi) ke DB per-request
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

# Base: class dasar untuk semua model (tabel)
Base = declarative_base()