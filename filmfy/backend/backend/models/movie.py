from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
)
from .meta import Base 

class Movie(Base):
    """
    Model SQLAlchemy untuk tabel 'movies'.
    Sudah cocok untuk digunakan dengan FormData/Upload Gambar.
    """
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    genre = Column(String(100), nullable=True)
    release_year = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True) 
    poster_path = Column(Text, nullable=True) 

    def to_dict(self, request=None): # <--- Perubahan: Ditambahkan 'request=None'
        """
        Mengembalikan representasi dictionary dari objek Movie.
        Jika 'request' diberikan, sertakan 'poster_url' yang lengkap.
        """
        poster_url = None
        # Periksa jika poster_path ada DAN objek request diberikan
        if self.poster_path and request:
            # Bangun URL lengkap: http://domain:port/static/path_relatif
            poster_url = f"{request.application_url}/static/{self.poster_path}"
        
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'release_year': self.release_year,
            'rating': self.rating,
            'poster_path': self.poster_path, 
            'poster_url': poster_url, # <--- Perubahan: Ditambahkan poster_url
        }