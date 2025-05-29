# from pyramid.config import Configurator


# def main(global_config, **settings):
#     """ This function returns a Pyramid WSGI application.
#     """
#     with Configurator(settings=settings) as config:
#         config.include('pyramid_jinja2')
#         config.include('.models')
#         config.include('.routes')
#     return config.make_wsgi_app()

from pyramid.config import Configurator
from pyramid.events import NewRequest # <--- Impor NewRequest
from pyramid.response import Response # <--- Impor Response

# Fungsi ini akan dipanggil untuk setiap request baru
def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        # Tambahkan header CORS ke SETIAP respons
        response.headers.update({
        'Access-Control-Allow-Origin': 'http://localhost:5173', # <-- Ganti '*' dengan origin Anda
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        })
    # Daftarkan callback yang akan dieksekusi sebelum respons dikirim
    event.request.add_response_callback(cors_headers)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('pyramid_beaker')
        config.include('.models')
        config.include('.routes') # Pastikan ini dipanggil SEBELUM subscriber jika rute ada di file lain

        # --- TAMBAHKAN SUBSCRIBER INI ---
        config.add_subscriber(add_cors_headers_response_callback, NewRequest)
        # --------------------------------

        # Pastikan Anda TIDAK punya config.scan() di sini jika 
        # Anda sudah scan di dalam routes.py

    return config.make_wsgi_app()
