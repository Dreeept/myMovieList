import os
import uuid
import shutil
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPCreated,
    HTTPNotFound,
    HTTPBadRequest,
    HTTPNoContent,
    HTTPUnauthorized # <--- Ditambahkan untuk proteksi
)

# Sesuaikan path import berdasarkan struktur proyek Anda
from ..models.movie import Movie

# --- Konfigurasi Direktori Upload ---
CURRENT_FILE_PATH = os.path.abspath(__file__)
VIEWS_DIR = os.path.dirname(CURRENT_FILE_PATH)
BACKEND_BACKEND_DIR = os.path.dirname(VIEWS_DIR)
POSTER_UPLOAD_DIR = os.path.join(BACKEND_BACKEND_DIR, 'static', 'postersMovie')
os.makedirs(POSTER_UPLOAD_DIR, exist_ok=True)

def _save_poster(poster_file_storage):
    """Helper function untuk menyimpan file poster dan mengembalikan nama filenya."""
    if (poster_file_storage is not None and
        hasattr(poster_file_storage, 'filename') and
        poster_file_storage.filename and
        hasattr(poster_file_storage, 'file')):
        _, ext = os.path.splitext(poster_file_storage.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        output_path = os.path.join(POSTER_UPLOAD_DIR, unique_filename)
        poster_file_storage.file.seek(0)
        with open(output_path, 'wb') as output_f:
            shutil.copyfileobj(poster_file_storage.file, output_f)
        return 'postersMovie/' + unique_filename
    return None

def _delete_poster(poster_path):
    """Helper function untuk menghapus file poster."""
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

# --- Fungsi Helper untuk Cek Session ---
def check_session(request):
    """Memeriksa apakah 'user_id' ada di session. Jika tidak, raise HTTPUnauthorized."""
    if 'user_id' not in request.session:
        raise HTTPUnauthorized(json_body={'error': 'Authentication required. Please log in.'})
    # Anda bisa menambahkan pengecekan lebih lanjut di sini jika perlu
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
            # ===> PANGGIL FUNGSI CEK SESSION DI SINI <===
            check_session(self.request)
            # ============================================

            title = self.request.POST['title']
            genre = self.request.POST.get('genre')
            release_year_str = self.request.POST.get('release_year')
            rating_str = self.request.POST.get('rating')
            poster_file = self.request.POST.get('poster')

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
            self.dbsession.flush()

            return HTTPCreated(json_body={
                'message': 'Movie created successfully!',
                'movie': new_movie.to_dict(request=self.request)
            })
        except HTTPUnauthorized as e: # <--- Tangkap error Unauthorized
            return e # <--- Kembalikan respons Unauthorized
        except KeyError as e:
            return HTTPBadRequest(json_body={'error': f'Missing form field: {e}'})
        except ValueError as e:
            return HTTPBadRequest(json_body={'error': f'Invalid data format: {e}'})
        except Exception as e:
            print(f"Error creating movie: {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- READ (TIDAK DIPROTEKSI - PUBLIK) ---
    @view_config(route_name='api_movies_list', request_method='GET')
    def list_movies(self):
        try:
            movies = self.dbsession.query(Movie).order_by(Movie.title).all()
            data = [movie.to_dict(request=self.request) for movie in movies]
            return data
        except Exception as e:
            print(f"Error listing movies: {e}")
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- READ (TIDAK DIPROTEKSI - PUBLIK) ---
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

    # --- UPDATE (DIPROTEKSI) ---
    @view_config(route_name='api_movie_update', request_method='POST')
    def update_movie(self):
        try:
            # ===> PANGGIL FUNGSI CEK SESSION DI SINI <===
            check_session(self.request)
            # ============================================

            movie_id = int(self.request.matchdict['id'])
            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                return HTTPNotFound(json_body={'error': 'Movie not found'})

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
        except HTTPUnauthorized as e: # <--- Tangkap error Unauthorized
            return e # <--- Kembalikan respons Unauthorized
        except ValueError as e:
            return HTTPBadRequest(json_body={'error': f'Invalid data format: {e}'})
        except Exception as e:
            print(f"ERROR: Updating movie - {e}")
            import traceback
            traceback.print_exc()
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}

    # --- DELETE (DIPROTEKSI) ---
    @view_config(route_name='api_movie_delete', request_method='DELETE')
    def delete_movie(self):
        try:
            # ===> PANGGIL FUNGSI CEK SESSION DI SINI <===
            check_session(self.request)
            # ============================================

            movie_id = int(self.request.matchdict['id'])
            movie = self.dbsession.query(Movie).get(movie_id)

            if not movie:
                return HTTPNotFound(json_body={'error': 'Movie not found'})

            if movie.poster_path:
                _delete_poster(movie.poster_path)

            self.dbsession.delete(movie)
            self.dbsession.flush()

            return HTTPNoContent()
        except HTTPUnauthorized as e: # <--- Tangkap error Unauthorized
            return e # <--- Kembalikan respons Unauthorized
        except ValueError:
            return HTTPBadRequest(json_body={'error': 'Invalid movie ID format'})
        except Exception as e:
            print(f"Error deleting movie: {e}")
            self.request.response.status_code = 500
            return {'error': f'An unexpected error occurred: {e}'}