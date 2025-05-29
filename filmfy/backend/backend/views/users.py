import os
import uuid
import shutil
import sqlalchemy.exc
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPOk, HTTPCreated, HTTPNotFound, HTTPBadRequest,
    HTTPConflict, HTTPUnauthorized, HTTPNoContent, HTTPForbidden # Ditambahkan HTTPForbidden
)
from ..models.user import User

# --- Konfigurasi Direktori Upload Foto Profil ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROFILE_PIC_UPLOAD_DIR = os.path.join(BACKEND_BACKEND_DIR, 'static', 'profile_pics')
os.makedirs(PROFILE_PIC_UPLOAD_DIR, exist_ok=True)

def _save_profile_photo(photo_file_storage):
    """Helper function untuk menyimpan foto profil."""
    if (photo_file_storage is not None and
            hasattr(photo_file_storage, 'filename') and
            photo_file_storage.filename):
        _, ext = os.path.splitext(photo_file_storage.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        output_path = os.path.join(PROFILE_PIC_UPLOAD_DIR, unique_filename)
        photo_file_storage.file.seek(0)
        with open(output_path, 'wb') as output_f:
            shutil.copyfileobj(photo_file_storage.file, output_f)
        return 'profile_pics/' + unique_filename # Simpan path relatif
    return None

def _delete_profile_photo(photo_path):
    """Helper function untuk menghapus foto profil."""
    if photo_path:
        actual_filename = photo_path.replace('profile_pics/', '', 1)
        full_path = os.path.join(PROFILE_PIC_UPLOAD_DIR, actual_filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError as e:
                print(f"Error deleting profile photo {full_path}: {e}")
                return False
    return False

# --- Fungsi untuk memeriksa otorisasi (Contoh) ---
def check_authorization(request, required_user_id):
    """Memeriksa apakah user yang login adalah user yang diminta."""
    if 'user_id' not in request.session:
        raise HTTPUnauthorized(json_body={'error': 'Authentication required.'})
    
    logged_in_user_id = request.session['user_id']
    if logged_in_user_id != required_user_id:
        raise HTTPForbidden(json_body={'error': 'You are not authorized for this action.'})
    
    return True

@view_defaults(renderer='json')
class UserViews:
    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession

    # --- SIGNUP ---
    @view_config(route_name='api_signup', request_method='POST')
    def signup_view(self):
        try:
            username = self.request.POST.get('username')
            email = self.request.POST.get('email')
            password = self.request.POST.get('password')
            confirm_password = self.request.POST.get('confirm_password')
            bio = self.request.POST.get('bio', None)
            foto_profil_storage = self.request.POST.get('foto_profil')

            if not all([username, email, password, confirm_password]):
                return HTTPBadRequest(json_body={'error': 'Username, email, password, and confirm password are required.'})

            if password != confirm_password:
                return HTTPBadRequest(json_body={'error': 'Passwords do not match.'})

            profile_photo_path = _save_profile_photo(foto_profil_storage)

            new_user = User(
                username=username,
                email=email,
                bio=bio,
                profile_photo=profile_photo_path
            )
            new_user.set_password(password)

            self.dbsession.add(new_user)
            self.dbsession.flush() # flush untuk mendapatkan ID user

            # --- *** LOGIN OTOMATIS & BUAT SESSION SETELAH SIGNUP *** ---
            session = self.request.session
            session['user_id'] = new_user.id # Simpan ID user ke session
            session.save()
            # -----------------------------------------------------------

            return HTTPCreated(json_body={
                'message': 'User created and logged in successfully!',
                'user': new_user.to_dict(request=self.request)
            })

        except sqlalchemy.exc.IntegrityError:
            self.dbsession.rollback()
            return HTTPConflict(json_body={'error': 'Username or email already exists.'})

        except Exception as e:
            self.dbsession.rollback()
            print(f"Error during signup: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- LOGIN (DIMODIFIKASI UNTUK SESSION) ---
    @view_config(route_name='api_login', request_method='POST')
    def login_view(self):
        try:
            json_data = self.request.json_body
            email = json_data.get('email')
            password = json_data.get('password')

            if not all([email, password]):
                return HTTPBadRequest(json_body={'error': 'Email and password are required.'})

            user = self.dbsession.query(User).filter_by(email=email).first()

            if not user or not user.check_password(password):
                return HTTPUnauthorized(json_body={'error': 'Invalid email or password.'})

            # --- *** INILAH MODIFIKASINYA: BUAT SESSION! *** ---
            session = self.request.session
            session['user_id'] = user.id  # Simpan ID user ke session
            session.save()               # Simpan session (Beaker akan mengirim cookie)
            # ----------------------------------------------------

            return HTTPOk(json_body={
                'message': 'Login successful!',
                'user': user.to_dict(request=self.request)
            })
        except Exception as e:
            print(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- LOGOUT ---
    @view_config(route_name='api_logout', request_method='POST', renderer='json')
    def logout_view(self):
        """Menghapus session pengguna dan cookie."""
        session = self.request.session
        session_key = self.request.registry.settings.get('session.key', 'session') # Ambil nama cookie dari .ini

        session.invalidate() # Hapus session di server

        # Hapus cookie di browser secara eksplisit
        self.request.response.delete_cookie(
            session_key, 
            path=self.request.registry.settings.get('session.cookie_path', '/'),
            domain=self.request.registry.settings.get('session.cookie_domain', None)
        )
        
        return HTTPOk(json_body={'message': 'Logout successful!'})

    # --- CHECK AUTH ---
    @view_config(route_name='api_check_auth', request_method='GET') # Tambahkan rute ini di routes.py
    def check_auth_view(self):
        """Memeriksa apakah pengguna memiliki session yang valid."""
        if 'user_id' in self.request.session:
            user_id = self.request.session['user_id']
            user = self.dbsession.query(User).get(user_id)
            if user:
                 return HTTPOk(json_body={'isAuthenticated': True, 'user': user.to_dict(request=self.request)})
        return HTTPOk(json_body={'isAuthenticated': False, 'user': None})


    # --- GET PROFILE (Sudah aman jika 'api_user_profile' tidak memerlukan auth) ---
    @view_config(route_name='api_user_profile', request_method='GET')
    def get_profile_view(self):
        try:
            user_id = int(self.request.matchdict['id'])
            user = self.dbsession.query(User).get(user_id)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})

            return HTTPOk(json_body=user.to_dict(request=self.request))
        except ValueError:
            return HTTPBadRequest(json_body={'error': 'Invalid user ID format'})
        except Exception as e:
            print(f"Error getting profile: {e}")
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- UPDATE PROFILE (DITAMBAHKAN CEK OTORISASI) ---
    @view_config(route_name='api_user_update', request_method='POST')
    def update_profile_view(self):
        try:
            user_id_to_update = int(self.request.matchdict['id'])
            
            # --- *** TAMBAHKAN PEMERIKSAAN OTORISASI *** ---
            check_authorization(self.request, user_id_to_update)
            # -----------------------------------------------

            user = self.dbsession.query(User).get(user_id_to_update)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})

            user.username = self.request.POST.get('username', user.username)
            user.email = self.request.POST.get('email', user.email)
            user.bio = self.request.POST.get('bio', user.bio)

            foto_profil_storage = self.request.POST.get('foto_profil')
            if (foto_profil_storage is not None and
                    hasattr(foto_profil_storage, 'filename') and
                    foto_profil_storage.filename):
                if user.profile_photo:
                    _delete_profile_photo(user.profile_photo)
                user.profile_photo = _save_profile_photo(foto_profil_storage)

            self.dbsession.flush()

            return HTTPOk(json_body={
                'message': 'Profile updated successfully!',
                'user': user.to_dict(request=self.request)
            })
        except (HTTPUnauthorized, HTTPForbidden) as auth_error:
            return auth_error # Kembalikan error otorisasi/autentikasi
        except sqlalchemy.exc.IntegrityError:
            self.dbsession.rollback()
            return HTTPConflict(json_body={'error': 'Username or email might already exist.'})
        except Exception as e:
            self.dbsession.rollback()
            print(f"Error updating profile: {e}")
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})

    # --- DELETE USER (DITAMBAHKAN CEK OTORISASI) ---
    @view_config(route_name='api_user_delete', request_method='DELETE')
    def delete_user_view(self):
        try:
            user_id_to_delete = int(self.request.matchdict['id'])

            # --- *** TAMBAHKAN PEMERIKSAAN OTORISASI *** ---
            check_authorization(self.request, user_id_to_delete)
            # -----------------------------------------------

            user = self.dbsession.query(User).get(user_id_to_delete)

            if not user:
                return HTTPNotFound(json_body={'error': 'User not found'})

            if user.profile_photo:
                _delete_profile_photo(user.profile_photo)

            self.dbsession.delete(user)
            self.dbsession.flush()
            
            # Hapus session juga saat delete
            self.request.session.invalidate()

            return HTTPNoContent()
        except (HTTPUnauthorized, HTTPForbidden) as auth_error:
            return auth_error # Kembalikan error otorisasi/autentikasi
        except Exception as e:
            self.dbsession.rollback()
            print(f"Error deleting user: {e}")
            return HTTPBadRequest(json_body={'error': f'An unexpected error occurred: {e}'})