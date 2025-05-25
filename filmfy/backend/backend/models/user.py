from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
)
from .meta import Base
# Hapus import passlib
# from passlib.context import CryptContext 
import bcrypt # <-- Impor bcrypt

# Hapus pwd_context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)
    bio = Column(Text, nullable=True)
    profile_photo = Column(Text, nullable=True) 

    def set_password(self, plain_password):
        """Mengambil password teks biasa dan menyimpannya sebagai hash menggunakan bcrypt."""
        # Ubah password menjadi bytes
        password_bytes = plain_password.encode('utf-8')
        # Generate salt
        salt = bcrypt.gensalt()
        # Hash password dengan salt
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        # Simpan hash sebagai string (bcrypt hash sudah aman untuk disimpan sebagai string)
        self.hashed_password = hashed_bytes.decode('utf-8')

    def check_password(self, plain_password):
        """Memverifikasi password teks biasa dengan hash yang tersimpan menggunakan bcrypt."""
        if self.hashed_password is None: # Jika belum ada hash (seharusnya tidak terjadi)
            return False
        # Ubah password input dan hash tersimpan menjadi bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = self.hashed_password.encode('utf-8')
        # Verifikasi
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    def to_dict(self, request=None):
        profile_url = None
        if self.profile_photo and request:
            profile_url = f"{request.application_url}/static/{self.profile_photo}"

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'profile_photo': self.profile_photo,
            'profile_url': profile_url,
        }