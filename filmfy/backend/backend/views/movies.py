import os
import uuid
import shutil
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPCreated, # Menggunakan HTTPCreated untuk respons POST yang berhasil
    HTTPNotFound,
    HTTPBadRequest,
    HTTPNoContent # Menggunakan HTTPNoContent untuk respons DELETE yang berhasil
)

# Sesuaikan path import berdasarkan struktur proyek Anda
# Jika movies.py ada di backend/backend/views/ dan movie.py ada di backend/backend/models/
from ..models.movie import Movie 

# --- Konfigurasi Direktori Upload ---
# Mendapatkan path absolut ke file movies.py saat ini
CURRENT_FILE_PATH = os.path.abspath(__file__)
# Mendapatkan direktori tempat movies.py berada (.../backend/backend/views/)
VIEWS_DIR = os.path.dirname(CURRENT_FILE_PATH)
# Naik satu level untuk mendapatkan direktori (.../backend/backend/)
BACKEND_BACKEND_DIR = os.path.dirname(VIEWS_DIR)
# Gabungkan dengan static dan nama folder yang Anda inginkan
POSTER_UPLOAD_DIR = os.path.join(BACKEND_BACKEND_DIR, 'static', 'postersMovie')


# Pastikan direktori upload ada
os.makedirs(POSTER_UPLOAD_DIR, exist_ok=True)

def _save_poster(poster_file_storage):
    """Helper function untuk menyimpan file poster dan mengembalikan nama filenya."""
    
    # --- PERUBAHAN DI SINI ---
    # Kita cek:
    # 1. Apakah objeknya BUKAN None?
    # 2. Apakah objeknya punya atribut 'filename'? (Menandakan ini FieldStorage untuk file)
    # 3. Apakah atribut 'filename'-nya TIDAK KOSONG? (Memastikan file benar-benar dipilih)
    # 4. (Opsional tapi aman) Apakah ia punya atribut 'file'?
    if (poster_file_storage is not None and 
        hasattr(poster_file_storage, 'filename') and 
        poster_file_storage.filename and 
        hasattr(poster_file_storage, 'file')):
    # --------------------------

        filename, ext = os.path.splitext(poster_file_storage.filename)
        # Buat nama file unik
        unique_filename = f"{uuid.uuid4()}{ext}"
        output_path = os.path.join(POSTER_UPLOAD_DIR, unique_filename)

        # Salin file yang diupload
        poster_file_storage.file.seek(0)
        with open(output_path, 'wb') as output_f:
            shutil.copyfileobj(poster_file_storage.file, output_f)
        return 'postersMovie/' + unique_filename # Simpan path relatif
        
    # Jika kondisi di atas tidak terpenuhi, berarti tidak ada file valid yang diupload
    return None

def _delete_poster(poster_path):
    """Helper function untuk menghapus file poster."""
    if poster_path:
        # Hapus prefix 'posters/' jika ada untuk mendapatkan nama file sebenarnya di direktori
        actual_filename = poster_path.replace('postersMovie/', '', 1)
        full_path = os.path.join(POSTER_UPLOAD_DIR, actual_filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError as e:
                # Log error jika diperlukan
                print(f"Error deleting poster file {full_path}: {e}")
                return False
    return False


@view_defaults(renderer='json') # Default renderer untuk semua view di class ini
class MovieViews:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    # --- CREATE (Membuat Movie Baru) ---
    @view_config(route_name='api_movies_create', request_method='POST')
    def create_movie(self):
        try:
            title = self.request.POST['title'] # Field wajib
            genre = self.request.POST.get('genre')
            release_year_str = self.request.POST.get('release_year')
            rating_str = self.request.POST.get('rating')
            poster_file = self.request.POST.get('poster')

            # Validasi dasar (bisa diperluas)
            if not title:
                raise HTTPBadRequest(json_body={'error': 'Title is required'})

            release_year = int(release_year_str) if release_year_str and release_year_str.isdigit() else None
            rating = int(rating_str) if rating_str and rating_str.isdigit() else None
            if rating is not None and not (1 <= rating <= 10):
                 raise HTTPBadRequest(json_body={'error': 'Rating must be between 1 and 10'})


            poster_path_rel = _save_poster(poster_file)

            new_movie = Movie(
                title=title,
                genre=genre,
                release_year=release_year,
                rating=rating,
                poster_path=poster_path_rel
            )
            self.dbsession.add(new_movie)
            self.dbsession.flush() # Untuk mendapatkan ID sebelum commit (jika diperlukan)
            
            # Menggunakan HTTPCreated (201) untuk respons yang berhasil membuat resource baru
            return HTTPCreated(json_body={
                'message': 'Movie created successfully!',
                'movie': new_movie.to_dict(request=self.request)
            })
        except KeyError as e:
            return HTTPBadRequest(json_body={'error': f'Missing form field: {e}'})
        except ValueError as e: # Untuk error konversi int
            return HTTPBadRequest(json_body={'error': f'Invalid data format: {e}'})
        except Exception as e:
            # Log error yang lebih detail di production
            print(f"Error creating movie: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500 # Internal Server Error
            return {'error': f'An unexpected error occurred: {e}'}

    # --- READ (Membaca Semua Movie) ---
    @view_config(route_name='api_movies_list', request_method='GET')
    def list_movies(self):
        try:
            movies = self.dbsession.query(Movie).order_by(Movie.title).all()
            # Menggunakan list comprehension dengan to_dict()
            data = [movie.to_dict(request=self.request) for movie in movies]
            return data # HTTPOk (200) adalah default jika tidak ada exception
        except Exception as e:
            print(f"Error listing movies: {e}")
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- READ (Membaca Satu Movie berdasarkan ID) ---
    @view_config(route_name='api_movie_detail', request_method='GET')
    def get_movie(self):
        try:
            movie_id = int(self.request.matchdict['id'])
            movie = self.dbsession.query(Movie).get(movie_id)
            if movie:
                return movie.to_dict(request=self.request)
            else:
                return HTTPNotFound(json_body={'error': 'Movie not found'})
        except ValueError:
            return HTTPBadRequest(json_body={'error': 'Invalid movie ID format'})
        except Exception as e:
            print(f"Error getting movie detail: {e}")
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- UPDATE (Memperbarui Movie berdasarkan ID) ---
    @view_config(route_name='api_movie_update', request_method='POST')
    def update_movie(self):
        try:
            movie_id = int(self.request.matchdict['id'])
            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                return HTTPNotFound(json_body={'error': 'Movie not found'})

            # Ambil data dari form, jika ada, update
            movie.title = self.request.POST.get('title', movie.title)
            movie.genre = self.request.POST.get('genre', movie.genre)
            
            release_year_str = self.request.POST.get('release_year')
            if release_year_str is not None:
                release_year_str = release_year_str.strip()
                movie.release_year = int(release_year_str) if release_year_str.isdigit() else movie.release_year

            rating_str = self.request.POST.get('rating')
            if rating_str is not None:
                rating_str = rating_str.strip()
                rating = int(rating_str) if rating_str.isdigit() else None
                if rating is not None:
                    if not (1 <= rating <= 10):
                        raise HTTPBadRequest(json_body={'error': 'Rating must be between 1 and 10'})
                    movie.rating = rating
                else:
                    movie.rating = movie.rating
            
            # --- Handle update poster (PERBAIKAN DI SINI) ---
            poster_file = self.request.POST.get('poster')
            
            # Gunakan pengecekan yang benar:
            if (poster_file is not None and 
                hasattr(poster_file, 'filename') and 
                poster_file.filename): # Cek jika filename ada dan tidak kosong

                print("DEBUG: File poster baru terdeteksi untuk update.")
                # Hapus poster lama jika ada
                if movie.poster_path:
                    _delete_poster(movie.poster_path)
                # Simpan poster baru
                movie.poster_path = _save_poster(poster_file) # _save_poster sudah benar
            # --------------------------------------------------

            self.dbsession.flush()
            return HTTPOk(json_body={
                'message': 'Movie updated successfully!',
                'movie': movie.to_dict(request=self.request) # Asumsi to_dict butuh request
            })
        except ValueError as e:
            return HTTPBadRequest(json_body={'error': f'Invalid data format: {e}'})
        except Exception as e:
            print(f"ERROR: Updating movie - {e}")
            import traceback
            traceback.print_exc() # Pastikan ini ada untuk melihat traceback lengkap
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- DELETE (Menghapus Movie berdasarkan ID) ---
    @view_config(route_name='api_movie_delete', request_method='DELETE')
    def delete_movie(self):
        try:
            movie_id = int(self.request.matchdict['id'])
            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                return HTTPNotFound(json_body={'error': 'Movie not found'})

            # Hapus file poster terkait jika ada
            if movie.poster_path:
                _delete_poster(movie.poster_path)

            self.dbsession.delete(movie)
            self.dbsession.flush() # Flush untuk memastikan delete berhasil
            
            # Menggunakan HTTPNoContent (204) untuk respons DELETE yang berhasil
            # HTTPNoContent tidak boleh memiliki body
            return HTTPNoContent() 
        except ValueError:
            return HTTPBadRequest(json_body={'error': 'Invalid movie ID format'})
        except Exception as e:
            print(f"Error deleting movie: {e}")
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}