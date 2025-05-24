# def includeme(config):
#     """
#     Fungsi ini menambahkan rute-rute API untuk movies
#     ke dalam konfigurasi Pyramid.
#     """
#     # Tambahkan static view untuk poster jika belum ada
#     config.add_static_view('static', 'static', cache_max_age=3600)
    
#     # Default route
#     config.add_route('home', '/')

#     # --- Rute untuk Movies ---
#     config.add_route('api_movies_create', '/api/movies', request_method='POST')
#     config.add_route('api_movies_list',   '/api/movies', request_method='GET')
#     config.add_route('api_movie_detail',  '/api/movies/{id:\d+}', request_method='GET')
#     config.add_route('api_movie_update',  '/api/movies/{id:\d+}', request_method='POST') 
#     config.add_route('api_movie_delete',  '/api/movies/{id:\d+}', request_method='DELETE')

#     # Pastikan view di-scan. Path ini mengasumsikan routes.py
#     # ada di backend/backend/ dan movies.py ada di backend/backend/views/
#     config.scan('.views.default')
#     config.scan('.views.movies')

from pyramid.response import Response

# View sederhana untuk OPTIONS
def options_view(request):
    return Response(status_code=204)

def includeme(config):
    """
    Fungsi ini menambahkan semua rute ke konfigurasi Pyramid.
    """
    config.add_static_view('static', 'static', cache_max_age=3600)

    # --- RUTE HOME (JANGAN HILANGKAN) ---
    config.add_route('home', '/')
    # ------------------------------------

    # --- Rute-rute CRUD Movies ---
    config.add_route('api_movies_create', '/api/movies', request_method='POST')
    config.add_route('api_movies_list',   '/api/movies', request_method='GET')
    config.add_route('api_movie_detail',  '/api/movies/{id:\d+}', request_method='GET')
    config.add_route('api_movie_update',  '/api/movies/{id:\d+}', request_method='POST')
    config.add_route('api_movie_delete',  '/api/movies/{id:\d+}', request_method='DELETE')
    # --- (Tambahkan rute API lain jika ada) ---

    # --- RUTE CATCH-ALL UNTUK CORS OPTIONS ---
    config.add_route('cors_preflight_catch_all', '/api/{catch_all:.*}', request_method='OPTIONS')
    config.add_view(options_view, route_name='cors_preflight_catch_all')
    # -----------------------------------------

    # --- Scan SEMUA Views Anda ---
    config.scan('.views.default') # <-- Pastikan ini ada
    config.scan('.views.movies')
    # --- (Scan view lain jika ada) ---