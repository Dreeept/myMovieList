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

    # --- RUTE-RUTE UNTUK USER (DITAMBAHKAN LOGOUT & CHECK_AUTH) ---
    config.add_route('api_signup', '/api/signup', request_method='POST')
    config.add_route('api_login', '/api/login', request_method='POST')
    config.add_route('api_logout', '/api/logout', request_method='POST') # <--- DITAMBAHKAN
    config.add_route('api_check_auth', '/api/check_auth', request_method='GET') # <--- DITAMBAHKAN
    config.add_route('api_user_profile', '/api/user/{id:\d+}', request_method='GET')
    config.add_route('api_user_update', '/api/user/{id:\d+}', request_method='POST')
    config.add_route('api_user_delete', '/api/user/{id:\d+}', request_method='DELETE')
    # -----------------------------

    # --- RUTE CATCH-ALL UNTUK CORS OPTIONS ---
    # Ini akan menangani preflight requests untuk SEMUA path di bawah /api/
    config.add_route('cors_preflight_catch_all', '/api/{catch_all:.*}', request_method='OPTIONS')
    config.add_view(options_view, route_name='cors_preflight_catch_all')
    # -----------------------------------------

    # --- Scan SEMUA Views Anda ---
    # Pastikan ini sesuai dengan nama file .py di dalam folder views Anda
    config.scan('.views.default') 
    config.scan('.views.movies')
    config.scan('.views.users') 
    # --- (Scan view lain jika ada) ---