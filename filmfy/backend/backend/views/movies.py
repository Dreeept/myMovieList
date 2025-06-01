import os
import uuid
import shutil
from pyramid.view import view_config, view_defaults
from pyramid.response import Response # Tidak terpakai, bisa dihapus jika tidak ada penggunaan lain
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPCreated,
    HTTPNotFound,
    HTTPBadRequest,
    HTTPNoContent,
    HTTPUnauthorized,
    HTTPException # <--- Tambahkan ini jika ingin menangkap semua HTTPException
)

# Sesuaikan path import berdasarkan struktur proyek Anda
from ..models.movie import Movie

# --- Konfigurasi Direktori Upload ---
# (Tidak ada perubahan di sini)
CURRENT_FILE_PATH = os.path.abspath(__file__)
VIEWS_DIR = os.path.dirname(CURRENT_FILE_PATH)
BACKEND_BACKEND_DIR = os.path.dirname(VIEWS_DIR)
POSTER_UPLOAD_DIR = os.path.join(BACKEND_BACKEND_DIR, 'static', 'postersMovie')
os.makedirs(POSTER_UPLOAD_DIR, exist_ok=True)

def _save_poster(poster_file_storage):
    # (Tidak ada perubahan di sini)
    if (poster_file_storage is not None and
        hasattr(poster_file_storage, 'filename') and
        poster_file_storage.filename and
        hasattr(poster_file_storage, 'file')):
        # Perbaikan untuk ValueError:
        filename, ext = os.path.splitext(poster_file_storage.filename)
        if not ext: # Jika tidak ada ekstensi, tambahkan default atau handle error
            # Untuk sementara, kita bisa set ekstensi default jika kosong,
            # atau Anda bisa raise error jika ekstensi diperlukan
            # contoh: ext = '.jpg' # jika ingin default
            pass # Biarkan ext kosong jika memang tidak ada dan itu valid

        unique_filename = f"{uuid.uuid4()}{ext}"
        output_path = os.path.join(POSTER_UPLOAD_DIR, unique_filename)
        poster_file_storage.file.seek(0)
        with open(output_path, 'wb') as output_f:
            shutil.copyfileobj(poster_file_storage.file, output_f)
        return 'postersMovie/' + unique_filename
    return None

def _delete_poster(poster_path):
    # (Tidak ada perubahan di sini)
    if poster_path:
        actual_filename = poster_path.replace('postersMovie/', '', 1)
        full_path = os.path.join(POSTER_UPLOAD_DIR, actual_filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError as e:
                print(f"Error deleting poster file {full_path}: {e}")
                return False
    return False

def check_session(request):
    # (Tidak ada perubahan di sini)
    if 'user_id' not in request.session:
        raise HTTPUnauthorized(json_body={'error': 'Authentication required. Please log in.'})
    return request.session['user_id']


@view_defaults(renderer='json')
class MovieViews:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    # --- CREATE (DIPROTEKSI) ---
    @view_config(route_name='api_movies_create', request_method='POST')
    def create_movie(self):
        try:
            check_session(self.request)

            title = self.request.POST['title']
            genre = self.request.POST.get('genre')
            release_year_str = self.request.POST.get('release_year')
            rating_str = self.request.POST.get('rating')
            poster_file = self.request.POST.get('poster')

            if not title:
                raise HTTPBadRequest(json_body={'error': 'Title is required'})

            release_year = int(release_year_str) if release_year_str and release_year_str.isdigit() else None
            rating = int(rating_str) if rating_str and rating_str.isdigit() else None
            
            # Validasi Rating
            if rating_str and not (rating_str.isdigit() and 1 <= int(rating_str) <= 10):
                 raise HTTPBadRequest(json_body={'error': 'Rating must be an integer between 1 and 10'})
            elif rating is not None and not (1 <= rating <= 10): # Jika sudah dikonversi dan masih di luar range
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
            self.dbsession.flush() # flush untuk mendapatkan ID jika diperlukan sebelum commit

            return HTTPCreated(json_body={
                'message': 'Movie created successfully!',
                'movie': new_movie.to_dict(request=self.request)
            })
        # ===== PERUBAHAN BLOK EXCEPT =====
        except (HTTPBadRequest, HTTPUnauthorized, HTTPNotFound) as e: # Tangkap HTTPException spesifik
            return e # Kembalikan objek HTTPException langsung
        except KeyError as e:
            # Ini akan menjadi HTTPBadRequest, jadi bisa digabung jika ingin konsisten
            return HTTPBadRequest(json_body={'error': f'Missing required form field: {e}'})
        except ValueError as e: # Misalnya untuk konversi int yang gagal jika tidak divalidasi baik
            return HTTPBadRequest(json_body={'error': f'Invalid data format for a field: {e}'})
        except Exception as e:
            # Log error yang lebih detail untuk server-side debugging
            # Anda mungkin ingin menggunakan logger aplikasi yang sebenarnya di sini
            print(f"UNEXPECTED ERROR in create_movie: {e}")
            import traceback
            traceback.print_exc()
            # Kembalikan respons error server yang umum
            self.request.response.status_code = 500 # Pastikan ini di-set jika mengembalikan dict manual
            return {'error': 'An unexpected server error occurred.'}
        # =================================

    # --- READ (TIDAK DIPROTEKSI - PUBLIK) ---
    @view_config(route_name='api_movies_list', request_method='GET')
    def list_movies(self):
        try:
            movies = self.dbsession.query(Movie).order_by(Movie.title).all()
            data = [movie.to_dict(request=self.request) for movie in movies]
            return data
        # ===== PERUBAHAN BLOK EXCEPT (JIKA PERLU PENANGANAN SPESIFIK) =====
        except Exception as e:
            print(f"UNEXPECTED ERROR in list_movies: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': 'An unexpected server error occurred while listing movies.'}
        # =================================

    # --- READ (TIDAK DIPROTEKSI - PUBLIK) ---
    @view_config(route_name='api_movie_detail', request_method='GET')
    def get_movie(self):
        try:
            movie_id_str = self.request.matchdict['id']
            if not movie_id_str.isdigit(): # Validasi ID adalah angka
                raise HTTPBadRequest(json_body={'error': 'Invalid movie ID format. ID must be an integer.'})
            movie_id = int(movie_id_str)
            
            movie = self.dbsession.query(Movie).get(movie_id)
            if movie:
                return movie.to_dict(request=self.request)
            else:
                # HTTPNotFound akan ditangkap oleh blok except HTTPException di bawah jika ada
                raise HTTPNotFound(json_body={'error': 'Movie not found'})
        # ===== PERUBAHAN BLOK EXCEPT =====
        except (HTTPBadRequest, HTTPNotFound) as e: # Tangkap HTTPException spesifik
            return e
        except ValueError: # Ini seharusnya sudah ditangani oleh isdigit() di atas
            return HTTPBadRequest(json_body={'error': 'Invalid movie ID format.'}) # Jaga-jaga
        except Exception as e:
            print(f"UNEXPECTED ERROR in get_movie: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': 'An unexpected server error occurred while fetching the movie.'}
        # =================================

    # --- UPDATE (DIPROTEKSI) ---
    @view_config(route_name='api_movie_update', request_method='POST')
    def update_movie(self):
        try:
            check_session(self.request)

            movie_id_str = self.request.matchdict['id']
            if not movie_id_str.isdigit(): # Validasi ID
                 raise HTTPBadRequest(json_body={'error': 'Invalid movie ID format. ID must be an integer.'})
            movie_id = int(movie_id_str)

            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                raise HTTPNotFound(json_body={'error': 'Movie not found'})

            # Ambil data dari POST, jika tidak ada, gunakan nilai yang sudah ada di movie
            movie.title = self.request.POST.get('title', movie.title).strip()
            if not movie.title: # Judul tidak boleh kosong setelah diupdate
                raise HTTPBadRequest(json_body={'error': 'Title cannot be empty'})

            movie.genre = self.request.POST.get('genre', movie.genre)
            if movie.genre is not None: # Pastikan string, bukan None yang di-strip
                 movie.genre = movie.genre.strip()


            release_year_str = self.request.POST.get('release_year')
            if release_year_str is not None: # Hanya proses jika ada input 'release_year'
                release_year_str = release_year_str.strip()
                if release_year_str: # Jika tidak kosong setelah strip
                    if not release_year_str.isdigit():
                        raise HTTPBadRequest(json_body={'error': 'Release year must be an integer.'})
                    movie.release_year = int(release_year_str)
                else: # Jika dikirim sebagai string kosong, set ke None atau biarkan (tergantung logika bisnis)
                    movie.release_year = None # Atau movie.release_year = movie.release_year

            rating_str = self.request.POST.get('rating')
            if rating_str is not None: # Hanya proses jika ada input 'rating'
                rating_str = rating_str.strip()
                if rating_str: # Jika tidak kosong setelah strip
                    if not rating_str.isdigit():
                        raise HTTPBadRequest(json_body={'error': 'Rating must be an integer.'})
                    rating = int(rating_str)
                    if not (1 <= rating <= 10):
                        raise HTTPBadRequest(json_body={'error': 'Rating must be between 1 and 10'})
                    movie.rating = rating
                else: # Jika dikirim sebagai string kosong, set ke None atau biarkan
                    movie.rating = None # Atau movie.rating = movie.rating


            poster_file = self.request.POST.get('poster')
            if (poster_file is not None and
                hasattr(poster_file, 'filename') and
                poster_file.filename):
                if movie.poster_path:
                    _delete_poster(movie.poster_path)
                movie.poster_path = _save_poster(poster_file)

            self.dbsession.flush()
            return HTTPOk(json_body={
                'message': 'Movie updated successfully!',
                'movie': movie.to_dict(request=self.request)
            })
        # ===== PERUBAHAN BLOK EXCEPT =====
        except (HTTPBadRequest, HTTPUnauthorized, HTTPNotFound) as e:
            return e
        except ValueError as e: # Untuk konversi int jika ada yang lolos validasi string
            return HTTPBadRequest(json_body={'error': f'Invalid data format: {e}'})
        except Exception as e:
            print(f"UNEXPECTED ERROR in update_movie: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': 'An unexpected server error occurred.'}
        # =================================

    # --- DELETE (DIPROTEKSI) ---
    @view_config(route_name='api_movie_delete', request_method='DELETE')
    def delete_movie(self):
        try:
            check_session(self.request)
            
            movie_id_str = self.request.matchdict['id']
            if not movie_id_str.isdigit(): # Validasi ID
                 raise HTTPBadRequest(json_body={'error': 'Invalid movie ID format. ID must be an integer.'})
            movie_id = int(movie_id_str)

            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                raise HTTPNotFound(json_body={'error': 'Movie not found'})

            if movie.poster_path:
                _delete_poster(movie.poster_path)

            self.dbsession.delete(movie)
            self.dbsession.flush()

            return HTTPNoContent() # HTTPNoContent biasanya tidak memiliki body
        # ===== PERUBAHAN BLOK EXCEPT =====
        except (HTTPBadRequest, HTTPUnauthorized, HTTPNotFound) as e:
            return e
        except ValueError: # Untuk konversi int jika ada yang lolos validasi string
            return HTTPBadRequest(json_body={'error': 'Invalid movie ID format.'}) # Jaga-jaga
        except Exception as e:
            print(f"UNEXPECTED ERROR in delete_movie: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': 'An unexpected server error occurred.'}
        # =================================